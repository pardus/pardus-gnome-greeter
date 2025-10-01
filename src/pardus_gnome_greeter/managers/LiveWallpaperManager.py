import os
import json
import requests
import threading
from datetime import datetime, timedelta
from gi.repository import GLib, Gio
from .settings import app_settings

class LiveWallpaperData:
    """Standardized wallpaper source data structure"""
    def __init__(self, source, title, description, image_url, thumbnail_url=None, 
                 filepath=None, status='pending', error_message=None):
        self.source = source
        self.title = title
        self.description = description
        self.image_url = image_url
        self.thumbnail_url = thumbnail_url or image_url  # Use full image if no thumbnail
        self.filepath = filepath
        self.status = status  # 'pending', 'downloading', 'available', 'error'
        self.error_message = error_message
        self.date = datetime.now().date()
    
    def to_dict(self):
        return {
            'source': self.source,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'thumbnail_url': self.thumbnail_url,
            'filepath': self.filepath,
            'status': self.status,
            'error_message': self.error_message,
            'date': self.date.isoformat()
        }
    
    @classmethod
    def from_api_response(cls, source_id, response_data, source_config):
        """Create LiveWallpaperData from any API response using source configuration"""
        try:
            mapping = source_config.get('response_mapping', {})
            validation = source_config.get('validation', {})
            
            # Validate response
            if not cls._validate_response(response_data, validation):
                return cls._create_error_instance(source_id, 'Invalid API response structure')
            
            # Navigate to data path if specified
            data = response_data
            data_path = mapping.get('data_path', '')
            if data_path:
                for key in data_path.split('.'):
                    if key.isdigit():
                        data = data[int(key)]
                    else:
                        data = data.get(key, {})
                    if not data:
                        return cls._create_error_instance(source_id, f'Data path not found: {data_path}')
            
            # Extract title
            title = cls._extract_field_value(data, mapping.get('title_keys', []), f'{source_id.title()} Wallpaper')
            
            # Apply title transformations
            title_transform = mapping.get('title_transform')
            if title_transform:
                title = cls._apply_transform(title, title_transform)
            
            # Extract description
            description = cls._extract_field_value(data, mapping.get('description_keys', []), '')
            
            # Extract image URL
            image_url = cls._extract_field_value(data, mapping.get('image_url_keys', []), '')
            if not image_url:
                return cls._create_error_instance(source_id, 'No image URL found in response')
            
            # Add URL prefix if specified
            url_prefix = mapping.get('image_url_prefix', '')
            if url_prefix and not image_url.startswith('http'):
                image_url = url_prefix + image_url
            
            # Extract or create thumbnail URL
            thumbnail_url = cls._extract_field_value(data, mapping.get('thumbnail_url_keys', []), image_url)
            
            # Apply thumbnail transformations
            thumbnail_transform = mapping.get('thumbnail_transform')
            if thumbnail_transform:
                thumbnail_url = cls._apply_transform(thumbnail_url, thumbnail_transform)
            
            return cls(
                source=source_id,
                title=title,
                description=description,
                image_url=image_url,
                thumbnail_url=thumbnail_url,
                status='pending'
            )
            
        except Exception as e:
            return cls._create_error_instance(source_id, f'Error parsing API response: {str(e)}')
    
    @staticmethod
    def _validate_response(response_data, validation):
        """Validate API response structure"""
        if not validation:
            return True
            
        # Check required fields
        required_fields = validation.get('required_fields', [])
        for field_path in required_fields:
            data = response_data
            for key in field_path.split('.'):
                if key.isdigit():
                    if not isinstance(data, list) or len(data) <= int(key):
                        return False
                    data = data[int(key)]
                else:
                    if not isinstance(data, dict) or key not in data:
                        return False
                    data = data[key]
        
        # Check media type if specified
        media_type_check = validation.get('media_type_check')
        if media_type_check:
            media_type = response_data.get('media_type', '')
            if media_type != media_type_check:
                return False
        
        return True
    
    @staticmethod
    def _extract_field_value(data, key_paths, default=''):
        """Extract field value using multiple possible key paths"""
        for key_path in key_paths:
            try:
                value = data
                for key in key_path.split('.'):
                    if key.isdigit():
                        value = value[int(key)]
                    else:
                        value = value[key]
                if value:
                    return str(value)
            except (KeyError, IndexError, TypeError):
                continue
        return default
    
    @staticmethod
    def _apply_transform(value, transform):
        """Apply transformation to a value"""
        if not transform or not value:
            return value
            
        transform_type = transform.get('type')
        
        if transform_type == 'replace':
            find = transform.get('find', '')
            replace = transform.get('replace', '')
            return value.replace(find, replace)
        elif transform_type == 'remove_prefix':
            prefix = transform.get('prefix', '')
            if value.startswith(prefix):
                return value[len(prefix):]
        elif transform_type == 'remove_suffix':
            suffix = transform.get('suffix', '')
            if value.endswith(suffix):
                return value[:-len(suffix)]
        
        return value
    
    @classmethod
    def _create_error_instance(cls, source, error_message):
        """Create an error instance of LiveWallpaperData"""
        return cls(
            source=source,
            title=f'{source.title()} Error',
            description='Failed to load wallpaper information',
            image_url='',
            status='error',
            error_message=error_message
        )

class LiveWallpaperManager:
    def __init__(self):
        # Load sources from JSON configuration
        self.sources = self._load_sources_config()
        
        # Cache directory - organized by date
        self.base_cache_dir = os.path.expanduser("~/.pardus-gnome-greeter/wallpapers")
        os.makedirs(self.base_cache_dir, exist_ok=True)
    
    def _load_sources_config(self):
        """Load wallpaper sources configuration from JSON file"""
        try:
            config_data = None
            
            # First try to load from GResource
            try:
                from gi.repository import Gio
                resource_path = '/tr/org/pardus/pardus-gnome-greeter/json/wallpaper_sources.json'
                resource = Gio.resources_lookup_data(resource_path, Gio.ResourceLookupFlags.NONE)
                if resource:
                    json_content = resource.get_data().decode('utf-8')
                    config_data = json.loads(json_content)
                    print("Loaded wallpaper sources from GResource")
            except Exception as e:
                print(f"Could not load from GResource: {e}")
            
            # Fallback to file system paths
            if not config_data:
                possible_paths = [
                    'data/json/wallpaper_sources.json',
                    '/usr/share/pardus-gnome-greeter/json/wallpaper_sources.json',
                    os.path.join(os.path.dirname(__file__), '../../data/json/wallpaper_sources.json')
                ]
                
                for config_path in possible_paths:
                    if os.path.exists(config_path):
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        print(f"Loaded wallpaper sources from {config_path}")
                        break
            
            if config_data and 'sources' in config_data:
                return config_data['sources']
            else:
                print("Warning: Could not load wallpaper sources config, using fallback")
                return self._get_fallback_sources()
                
        except Exception as e:
            print(f"Error loading wallpaper sources config: {e}")
            return self._get_fallback_sources()
    
    def _get_fallback_sources(self):
        """Fallback sources configuration if JSON file is not available"""
        return {
            'bing': {
                'name': 'Bing Daily',
                'description': 'Microsoft Bing daily wallpapers',
                'enabled': True,
                'api_url': 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US',
                'headers': {},
                'response_mapping': {
                    'data_path': 'images.0',
                    'title_keys': ['title'],
                    'description_keys': ['copyright'],
                    'image_url_keys': ['url'],
                    'image_url_prefix': 'https://www.bing.com',
                    'thumbnail_transform': {
                        'type': 'replace',
                        'find': '1920x1080',
                        'replace': '480x270'
                    }
                },
                'validation': {
                    'required_fields': ['images'],
                    'image_check': 'images.0.url'
                }
            }
        }
    
    def get_daily_cache_dir(self, date=None):
        """Get cache directory for specific date"""
        if date is None:
            date = datetime.now()
        
        # Format: DD.MM.YYYY
        date_str = date.strftime('%d.%m.%Y')
        daily_dir = os.path.join(self.base_cache_dir, date_str)
        os.makedirs(daily_dir, exist_ok=True)
        return daily_dir
    
    def sanitize_filename(self, title):
        """Sanitize title for filename"""
        # Remove/replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '')
        
        # Replace spaces with underscores and limit length
        title = title.replace(' ', '_')
        title = title[:50]  # Limit to 50 characters
        
        return title
    
    def get_wallpaper_filename(self, source, title, ext, date=None):
        """Generate wallpaper filename with source, title and extension"""
        if date is None:
            date = datetime.now()
            
        sanitized_title = self.sanitize_filename(title)
        filename = f"{source}-{sanitized_title}.{ext}"
        
        daily_dir = self.get_daily_cache_dir(date)
        return os.path.join(daily_dir, filename)
        
    def is_enabled(self):
        """Check if live wallpapers are enabled"""
        try:
            return app_settings.get('live-wallpaper-enabled')
        except:
            return False
    
    def set_enabled(self, enabled):
        """Enable or disable live wallpapers"""
        try:
            app_settings.set('live-wallpaper-enabled', enabled)
            return True
        except Exception as e:
            print(f"Error setting live wallpaper enabled: {e}")
            return False
    
    def get_selected_sources(self):
        """Get list of selected sources"""
        try:
            sources_json = app_settings.get('live-wallpaper-sources')
            if sources_json:
                return json.loads(sources_json)
            return ['bing']  # Default
        except:
            return ['bing']
    
    def set_selected_sources(self, sources):
        """Set selected sources"""
        try:
            sources_json = json.dumps(sources)
            app_settings.set('live-wallpaper-sources', sources_json)
            return True
        except Exception as e:
            print(f"Error setting sources: {e}")
            return False
    
    def get_shuffle_interval(self):
        """Get shuffle interval in minutes for cycling between sources"""
        try:
            return app_settings.get('live-wallpaper-shuffle-interval')
        except:
            return 30  # Default 30 minutes
    
    def set_shuffle_interval(self, minutes):
        """Set shuffle interval in minutes for cycling between sources"""
        try:
            app_settings.set('live-wallpaper-shuffle-interval', minutes)
            return True
        except Exception as e:
            print(f"Error setting shuffle interval: {e}")
            return False
    
    def get_last_check_date(self):
        """Get last daily check date (YYYY-MM-DD format)"""
        try:
            date_str = app_settings.get('live-wallpaper-last-check-date')
            if date_str:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            return None
        except:
            return None
    
    def set_last_check_date(self, date=None):
        """Set last daily check date"""
        try:
            if date is None:
                date = datetime.now().date()
            date_str = date.strftime('%Y-%m-%d')
            app_settings.set('live-wallpaper-last-check-date', date_str)
            return True
        except Exception as e:
            print(f"Error setting last check date: {e}")
            return False
    
    def get_current_source_index(self):
        """Get current source index for cycling"""
        try:
            return app_settings.get('live-wallpaper-current-source-index')
        except:
            return 0
    
    def set_current_source_index(self, index):
        """Set current source index for cycling"""
        try:
            app_settings.set('live-wallpaper-current-source-index', index)
            return True
        except Exception as e:
            print(f"Error setting current source index: {e}")
            return False
    
    def should_check_daily_wallpapers(self):
        """Check if we should download today's wallpapers (once per day)"""
        if not self.is_enabled():
            return False
            
        last_check = self.get_last_check_date()
        today = datetime.now().date()
        
        return last_check != today
    
    def should_cycle_wallpaper(self):
        """Check if we should cycle to next wallpaper (for multiple sources)"""
        if not self.is_enabled():
            return False
            
        selected_sources = self.get_selected_sources()
        if len(selected_sources) <= 1:
            return False  # No cycling needed for single source
            
        # Check if enough time has passed for cycling
        try:
            last_cycle_str = app_settings.get('live-wallpaper-last-cycle')
            if last_cycle_str:
                last_cycle = datetime.fromisoformat(last_cycle_str)
                interval_minutes = self.get_shuffle_interval()
                next_cycle = last_cycle + timedelta(minutes=interval_minutes)
                return datetime.now() >= next_cycle
            return True  # First cycle
        except:
            return True
    
    def get_available_sources(self):
        """Get all available wallpaper sources"""
        return self.sources
    
    def normalize_bing_response(self, response_data):
        """Convert Bing API response to LiveWallpaperData"""
        if 'bing' in self.sources:
            return LiveWallpaperData.from_api_response('bing', response_data, self.sources['bing'])
        return LiveWallpaperData._create_error_instance('bing', 'Bing source not configured')
    
    def normalize_nasa_response(self, response_data):
        """Convert NASA API response to LiveWallpaperData"""
        if 'nasa' in self.sources:
            return LiveWallpaperData.from_api_response('nasa', response_data, self.sources['nasa'])
        return LiveWallpaperData._create_error_instance('nasa', 'NASA source not configured')
    
    def normalize_wikipedia_response(self, response_data):
        """Convert Wikipedia API response to LiveWallpaperData"""
        if 'wikipedia' in self.sources:
            return LiveWallpaperData.from_api_response('wikipedia', response_data, self.sources['wikipedia'])
        return LiveWallpaperData._create_error_instance('wikipedia', 'Wikipedia source not configured')
    
    def fetch_wallpaper_info(self, source):
        """Fetch and normalize wallpaper info from any source (backward compatibility)"""
        return self.fetch_wallpaper_info_from_source(source)
    
    def fetch_wallpaper_info_from_source(self, source_id):
        """Fetch wallpaper info from any source using JSON configuration"""
        if source_id not in self.sources:
            return LiveWallpaperData._create_error_instance(source_id, 'Unknown source')
        
        source_config = self.sources[source_id]
        
        try:
            # Prepare API URL (handle dynamic URLs like Wikipedia)
            api_url = source_config['api_url']
            if '{year}' in api_url or '{month}' in api_url or '{day}' in api_url:
                today = datetime.now()
                api_url = api_url.format(
                    year=today.year,
                    month=today.month,
                    day=today.day
                )
            
            # Prepare headers
            headers = source_config.get('headers', {})
            
            # Check if this is a direct image API
            response_mapping = source_config.get('response_mapping', {})
            if response_mapping.get('direct_image', False):
                # For direct image APIs, just return the URL
                return LiveWallpaperData(
                    source=source_id,
                    title=f'{source_config["name"]} Image',
                    description=source_config.get('description', ''),
                    image_url=api_url,
                    thumbnail_url=api_url,
                    status='pending'
                )
            
            # Make API request for JSON response
            response = requests.get(api_url, headers=headers, timeout=10)
            data = response.json()
            
            # Create normalized data using JSON configuration
            return LiveWallpaperData.from_api_response(source_id, data, source_config)
            
        except Exception as e:
            print(f"Error fetching {source_id} wallpaper info: {e}")
            return LiveWallpaperData._create_error_instance(source_id, f'Network error: {str(e)}')
    
    def download_wallpaper_from_source(self, source_id):
        """Download wallpaper from any source using JSON configuration"""
        try:
            # First get wallpaper info
            wallpaper_data = self.fetch_wallpaper_info_from_source(source_id)
            if not wallpaper_data or wallpaper_data.status == 'error':
                return wallpaper_data.to_dict() if wallpaper_data else None
            
            # Update status to downloading
            wallpaper_data.status = 'downloading'
            
            # Get source configuration for headers
            source_config = self.sources.get(source_id, {})
            headers = source_config.get('headers', {})
            
            # Download image
            img_response = requests.get(wallpaper_data.image_url, headers=headers, timeout=30)
            if img_response.status_code == 200:
                # Get file extension from URL
                ext = wallpaper_data.image_url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    ext = 'jpg'
                
                # Generate organized filename
                filepath = self.get_wallpaper_filename(source_id, wallpaper_data.title, ext)
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                wallpaper_data.filepath = filepath
                wallpaper_data.status = 'available'
                return wallpaper_data.to_dict()
            else:
                wallpaper_data.status = 'error'
                wallpaper_data.error_message = f'Download failed with status {img_response.status_code}'
                return wallpaper_data.to_dict()
                
        except Exception as e:
            print(f"Error downloading {source_id} wallpaper: {e}")
            error_data = LiveWallpaperData._create_error_instance(source_id, f'Download error: {str(e)}')
            return error_data.to_dict()
    

    
    def download_daily_wallpapers(self):
        """Download today's wallpapers from all selected sources"""
        if not self.should_check_daily_wallpapers():
            return True  # Already have today's wallpapers
        
        selected_sources = self.get_selected_sources()
        if not selected_sources:
            return False
        
        downloaded_any = False
        
        # Download from all selected sources
        for source in selected_sources:
            wallpaper_info = self.download_wallpaper_from_source(source)
            if wallpaper_info:
                downloaded_any = True
                print(f"Downloaded daily wallpaper from {source}: {wallpaper_info['title']}")
        
        if downloaded_any:
            self.set_last_check_date()
            # Set first wallpaper immediately
            self.cycle_wallpaper()
        
        return downloaded_any
    
    def cycle_wallpaper(self):
        """Cycle to next wallpaper from available sources"""
        selected_sources = self.get_selected_sources()
        if not selected_sources:
            return False
        
        # Get current source index
        current_index = self.get_current_source_index()
        if current_index >= len(selected_sources):
            current_index = 0
        
        # Try to set wallpaper from current source
        source = selected_sources[current_index]
        
        wallpaper_set = False
        daily_dir = self.get_daily_cache_dir()
        
        try:
            # Look for today's wallpapers with new naming format
            if os.path.exists(daily_dir):
                for source_file in os.listdir(daily_dir):
                    if source_file.startswith(f"{source}-") and source_file.endswith(('.jpg', '.jpeg', '.png')):
                        filepath = os.path.join(daily_dir, source_file)
                        try:
                            from .WallpaperManager import WallpaperManager
                            wallpaper_manager = WallpaperManager()
                            success = wallpaper_manager.set_wallpaper(filepath)
                            
                            if success:
                                print(f"Cycled to wallpaper from {source}: {source_file}")
                                wallpaper_set = True
                                break
                        except Exception as e:
                            print(f"Error setting wallpaper: {e}")
        except Exception as e:
            print(f"Error accessing daily cache directory: {e}")
        
        if wallpaper_set:
            # Update cycle timestamp
            try:
                app_settings.set('live-wallpaper-last-cycle', datetime.now().isoformat())
            except:
                pass
            
            # Move to next source for next cycle
            next_index = (current_index + 1) % len(selected_sources)
            self.set_current_source_index(next_index)
            
            return True
        
        return False
    
    def update_wallpaper_now(self):
        """Force update wallpaper now (for manual update button)"""
        # First ensure we have today's wallpapers
        self.download_daily_wallpapers()
        
        # Then cycle to next wallpaper
        return self.cycle_wallpaper()
    
    def start_background_service(self):
        """Start background service for automatic wallpaper updates"""
        def daily_check():
            """Check for daily wallpapers once per day"""
            if self.should_check_daily_wallpapers():
                threading.Thread(target=self.download_daily_wallpapers, daemon=True).start()
            
            # Schedule next daily check in 1 hour
            GLib.timeout_add_seconds(3600, daily_check)
            return False
        
        def cycle_check():
            """Check for wallpaper cycling (for multiple sources)"""
            if self.should_cycle_wallpaper():
                threading.Thread(target=self.cycle_wallpaper, daemon=True).start()
            
            # Schedule next cycle check based on interval
            interval_minutes = self.get_shuffle_interval()
            GLib.timeout_add_seconds(interval_minutes * 60, cycle_check)
            return False
        
        # Initial checks
        GLib.timeout_add_seconds(5, daily_check)  # Daily check after 5 seconds
        GLib.timeout_add_seconds(10, cycle_check)  # Cycle check after 10 seconds