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
            
            # Validate thumbnail URL (Reddit sometimes returns "self", "default", etc.)
            if thumbnail_url and not thumbnail_url.startswith('http'):
                thumbnail_url = image_url  # Fallback to main image
            
            # Apply thumbnail transformations
            thumbnail_transform = mapping.get('thumbnail_transform')
            if thumbnail_transform and thumbnail_url:
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
            'reddit': {
                'name': 'Reddit Wallpapers',
                'description': 'Top wallpapers from r/wallpaper',
                'enabled': True,
                'api_url': 'https://www.reddit.com/r/wallpaper/top.json?t=day&limit=1',
                'headers': {
                    'User-Agent': 'PardusGnomeGreeter/1.0 (https://github.com/pardus/pardus-gnome-greeter)'
                },
                'response_mapping': {
                    'data_path': 'data.children.0.data',
                    'title_keys': ['title'],
                    'description_keys': ['subreddit_name_prefixed'],
                    'image_url_keys': ['url'],
                    'thumbnail_url_keys': ['thumbnail'],
                    'image_url_prefix': ''
                },
                'validation': {
                    'required_fields': ['data.children']
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
    
    def get_metadata_filepath(self, source_id, title=None, date=None):
        """Get metadata JSON filepath for a wallpaper"""
        daily_dir = self.get_daily_cache_dir(date)
        filename = f"{source_id}.json"
        return os.path.join(daily_dir, filename)
    
    def save_metadata(self, wallpaper_data):
        """Save wallpaper metadata to JSON file"""
        try:
            if not wallpaper_data or not wallpaper_data.title:
                return False
            
            metadata_path = self.get_metadata_filepath(
                wallpaper_data.source,
                wallpaper_data.title
            )
            
            # Prepare metadata dict
            metadata = {
                'source': wallpaper_data.source,
                'title': wallpaper_data.title,
                'description': wallpaper_data.description,
                'image_url': wallpaper_data.image_url,
                'thumbnail_url': wallpaper_data.thumbnail_url,
                'filepath': wallpaper_data.filepath,
                'status': wallpaper_data.status,
                'date': wallpaper_data.date.isoformat() if hasattr(wallpaper_data.date, 'isoformat') else str(wallpaper_data.date),
                'fetched_at': datetime.now().isoformat(),
                'error_message': wallpaper_data.error_message
            }
            
            # Write to file
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"Saved metadata for {wallpaper_data.source}: {metadata_path}")
            return True
            
        except Exception as e:
            print(f"Error saving metadata: {e}")
            return False
    
    def load_metadata(self, source_id, date=None):
        """Load wallpaper metadata from JSON file"""
        try:
            # Try direct filename first (new format)
            metadata_path = self.get_metadata_filepath(source_id, date=date)
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Create LiveWallpaperData from metadata
                wallpaper_data = LiveWallpaperData(
                    source=metadata.get('source', source_id),
                    title=metadata.get('title', ''),
                    description=metadata.get('description', ''),
                    image_url=metadata.get('image_url', ''),
                    thumbnail_url=metadata.get('thumbnail_url', ''),
                    filepath=metadata.get('filepath'),
                    status=metadata.get('status', 'pending'),
                    error_message=metadata.get('error_message')
                )
                
                print(f"Loaded metadata for {source_id} from cache")
                return wallpaper_data
            
            # Fallback: search for old format files (source_id-title.json)
            daily_dir = self.get_daily_cache_dir(date)
            if os.path.exists(daily_dir):
                for filename in os.listdir(daily_dir):
                    if filename.startswith(f"{source_id}-") and filename.endswith('.json'):
                        metadata_path = os.path.join(daily_dir, filename)
                        
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        wallpaper_data = LiveWallpaperData(
                            source=metadata.get('source', source_id),
                            title=metadata.get('title', ''),
                            description=metadata.get('description', ''),
                            image_url=metadata.get('image_url', ''),
                            thumbnail_url=metadata.get('thumbnail_url', ''),
                            filepath=metadata.get('filepath'),
                            status=metadata.get('status', 'pending'),
                            error_message=metadata.get('error_message')
                        )
                        
                        print(f"Loaded metadata for {source_id} from cache (old format)")
                        return wallpaper_data
            
            return None
            
        except Exception as e:
            print(f"Error loading metadata for {source_id}: {e}")
            return None
    
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
            return ['reddit']  # Default
        except:
            return ['reddit']
    
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
            result = app_settings.set('live-wallpaper-shuffle-interval', int(minutes))
            if result is False:
                print(f"Failed to set shuffle interval to {minutes}")
                return False
            print(f"Shuffle interval set to {minutes} minutes")
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
    
    def _get_api_error_message(self, source_id, status_code):
        """Get user-friendly error message for API HTTP status codes"""
        source_name = self.sources.get(source_id, {}).get('name', source_id)
        
        if status_code == 429:
            return f'{source_name} rate limit exceeded - please try again later'
        elif status_code == 403:
            return f'{source_name} access forbidden - API key may be invalid'
        elif status_code == 404:
            return f'{source_name} not found - no wallpaper available today'
        elif status_code == 500:
            return f'{source_name} server error - please try again later'
        elif status_code == 503:
            return f'{source_name} service unavailable - please try again later'
        elif 400 <= status_code < 500:
            return f'{source_name} client error (HTTP {status_code})'
        elif 500 <= status_code < 600:
            return f'{source_name} server error (HTTP {status_code})'
        else:
            return f'{source_name} error (HTTP {status_code})'
    
    def fetch_wallpaper_info(self, source):
        """Fetch and normalize wallpaper info from any source (backward compatibility)"""
        return self.fetch_wallpaper_info_from_source(source)
    
    def fetch_wallpaper_info_from_source(self, source_id, force_refresh=False):
        """Fetch wallpaper info from any source using JSON configuration
        
        Args:
            source_id: Source identifier
            force_refresh: If True, bypass cache and fetch from API
        """
        if source_id not in self.sources:
            return LiveWallpaperData._create_error_instance(source_id, 'Unknown source')
        
        # Try to load from cache first (unless force refresh)
        if not force_refresh:
            cached_data = self.load_metadata(source_id)
            if cached_data:
                print(f"Using cached metadata for {source_id} - no API request needed")
                return cached_data
        
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
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = self._get_api_error_message(source_id, response.status_code)
                return LiveWallpaperData._create_error_instance(source_id, error_msg)
            
            data = response.json()
            
            # Create normalized data using JSON configuration
            wallpaper_data = LiveWallpaperData.from_api_response(source_id, data, source_config)
            
            # Don't save metadata here - it will be saved after successful download
            # in download_wallpaper_from_source()
            
            return wallpaper_data
            
        except requests.exceptions.Timeout:
            return LiveWallpaperData._create_error_instance(source_id, 'Request timeout - server not responding')
        except requests.exceptions.ConnectionError:
            return LiveWallpaperData._create_error_instance(source_id, 'Connection error - check your internet')
        except requests.exceptions.RequestException as e:
            return LiveWallpaperData._create_error_instance(source_id, f'Network error: {str(e)}')
        except Exception as e:
            print(f"Error fetching {source_id} wallpaper info: {e}")
            return LiveWallpaperData._create_error_instance(source_id, f'Error: {str(e)}')
    
    def download_wallpaper_from_source(self, source_id, progress_callback=None):
        """Download wallpaper from any source using JSON configuration
        
        Args:
            source_id: Source identifier
            progress_callback: Optional callback function(current, total) for progress updates
        """
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
            
            # Download image with progress tracking
            print(f"Downloading image from: {wallpaper_data.image_url}")
            img_response = requests.get(wallpaper_data.image_url, headers=headers, timeout=30, stream=True)
            
            if img_response.status_code == 200:
                # Get file extension from URL
                ext = wallpaper_data.image_url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    ext = 'jpg'
                
                # Generate organized filename
                filepath = self.get_wallpaper_filename(source_id, wallpaper_data.title, ext)
                print(f"Saving to: {filepath}")
                
                # Get total file size
                total_size = int(img_response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(filepath, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # Call progress callback if provided
                            if progress_callback and total_size > 0:
                                progress_callback(downloaded_size, total_size)
                
                # Verify file was created
                if not os.path.exists(filepath):
                    print(f"Error: File was not created: {filepath}")
                    wallpaper_data.status = 'error'
                    wallpaper_data.error_message = 'File creation failed'
                    return wallpaper_data.to_dict()
                
                wallpaper_data.filepath = filepath
                wallpaper_data.status = 'available'
                
                # Update metadata with filepath
                self.save_metadata(wallpaper_data)
                print(f"✓ Successfully downloaded: {filepath}")
                
                return wallpaper_data.to_dict()
            else:
                print(f"✗ Download failed with status {img_response.status_code}")
                wallpaper_data.status = 'error'
                error_msg = self._get_api_error_message(source_id, img_response.status_code)
                wallpaper_data.error_message = error_msg
                # Don't save metadata for failed downloads
                return wallpaper_data.to_dict()
                
        except requests.exceptions.Timeout:
            error_data = LiveWallpaperData._create_error_instance(source_id, 'Download timeout - file too large or slow connection')
            return error_data.to_dict()
        except requests.exceptions.ConnectionError:
            error_data = LiveWallpaperData._create_error_instance(source_id, 'Connection error - check your internet')
            return error_data.to_dict()
        except IOError as e:
            error_data = LiveWallpaperData._create_error_instance(source_id, f'File write error: {str(e)}')
            return error_data.to_dict()
        except Exception as e:
            print(f"Error downloading {source_id} wallpaper: {e}")
            error_data = LiveWallpaperData._create_error_instance(source_id, f'Download error: {str(e)}')
            return error_data.to_dict()
    

    
    def download_daily_wallpapers(self):
        """Download today's wallpapers from all selected sources"""
        print("Checking if daily wallpapers need to be downloaded...")
        
        if not self.should_check_daily_wallpapers():
            print("Today's wallpapers already checked, skipping download")
            return True  # Already have today's wallpapers
        
        selected_sources = self.get_selected_sources()
        print(f"Selected sources for download: {selected_sources}")
        
        if not selected_sources:
            print("No sources selected!")
            return False
        
        downloaded_any = False
        
        # Download from all selected sources
        for source in selected_sources:
            print(f"--- Downloading from {source} ---")
            wallpaper_info = self.download_wallpaper_from_source(source)
            
            if wallpaper_info:
                status = wallpaper_info.get('status')
                print(f"Download result for {source}: status={status}")
                
                if status == 'available':
                    downloaded_any = True
                    print(f"✓ Downloaded daily wallpaper from {source}: {wallpaper_info.get('title')}")
                else:
                    print(f"✗ Failed to download from {source}: {wallpaper_info.get('error_message')}")
            else:
                print(f"✗ No wallpaper info returned from {source}")
        
        if downloaded_any:
            print("Setting last check date...")
            self.set_last_check_date()
            # Set first wallpaper immediately
            print("Setting first wallpaper...")
            self.cycle_wallpaper()
        else:
            print("No wallpapers were downloaded successfully")
        
        return downloaded_any
    
    def cycle_wallpaper(self):
        """Cycle to next wallpaper from available sources"""
        selected_sources = self.get_selected_sources()
        print(f"Selected sources: {selected_sources}")
        
        if not selected_sources:
            print("No sources selected!")
            return False
        
        # Get current source index
        current_index = self.get_current_source_index()
        if current_index >= len(selected_sources):
            current_index = 0
        
        # Try to set wallpaper from current source
        source = selected_sources[current_index]
        print(f"Trying to cycle from source: {source} (index: {current_index})")
        
        wallpaper_set = False
        daily_dir = self.get_daily_cache_dir()
        print(f"Daily cache directory: {daily_dir}")
        
        try:
            # Look for today's wallpapers with new naming format
            if os.path.exists(daily_dir):
                files = os.listdir(daily_dir)
                print(f"Files in cache: {files}")
                
                for source_file in files:
                    if source_file.startswith(f"{source}-") and source_file.endswith(('.jpg', '.jpeg', '.png')):
                        filepath = os.path.join(daily_dir, source_file)
                        print(f"Found wallpaper file: {filepath}")
                        
                        try:
                            from .WallpaperManager import WallpaperManager
                            wallpaper_manager = WallpaperManager()
                            success = wallpaper_manager.set_wallpaper(filepath)
                            
                            if success:
                                print(f"✓ Cycled to wallpaper from {source}: {source_file}")
                                wallpaper_set = True
                                break
                            else:
                                print(f"✗ Failed to set wallpaper: {filepath}")
                        except Exception as e:
                            print(f"✗ Error setting wallpaper: {e}")
                
                if not wallpaper_set:
                    print(f"No wallpaper file found for source: {source}")
            else:
                print(f"Daily cache directory does not exist: {daily_dir}")
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
        
        print("Failed to cycle wallpaper")
        return False
    
    def update_wallpaper_now(self):
        """Force update wallpaper now (for manual update button)"""
        print("=== Manual wallpaper update requested ===")
        
        # Force download today's wallpapers (bypass daily check)
        print("Force downloading today's wallpapers...")
        selected_sources = self.get_selected_sources()
        
        if not selected_sources:
            print("No sources selected!")
            return False
        
        downloaded_any = False
        
        # Download from all selected sources
        for source in selected_sources:
            print(f"--- Downloading from {source} ---")
            wallpaper_info = self.download_wallpaper_from_source(source)
            
            if wallpaper_info:
                status = wallpaper_info.get('status')
                print(f"Download result for {source}: status={status}")
                
                if status == 'available':
                    downloaded_any = True
                    print(f"✓ Downloaded from {source}: {wallpaper_info.get('title')}")
                else:
                    print(f"✗ Failed to download from {source}: {wallpaper_info.get('error_message')}")
            else:
                print(f"✗ No wallpaper info returned from {source}")
        
        if downloaded_any:
            print("Setting last check date...")
            self.set_last_check_date()
        
        # Then cycle to next wallpaper
        print("Cycling to next wallpaper...")
        cycle_result = self.cycle_wallpaper()
        print(f"Cycle result: {cycle_result}")
        print(f"=== Update completed: {cycle_result} ===")
        
        return cycle_result
    
    def start_background_service(self):
        """Ensure background daemon service is running
        
        Note: Daemon is started automatically via autostart desktop file.
        This method just ensures it's running if user manually enabled live wallpaper.
        Settings changes are automatically propagated via GSettings/D-Bus.
        """
        import os
        
        try:
            # Check if we're in a session where daemon can run
            if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
                print("No display session, daemon cannot be started")
                return False
            
            # Check if daemon is already running by looking at /proc
            daemon_running = False
            try:
                for pid_dir in os.listdir('/proc'):
                    if not pid_dir.isdigit():
                        continue
                    try:
                        cmdline_path = f'/proc/{pid_dir}/cmdline'
                        with open(cmdline_path, 'r') as f:
                            cmdline = f.read()
                            if 'pardus-gnome-greeter' in cmdline and '--daemon' in cmdline:
                                daemon_running = True
                                break
                    except (FileNotFoundError, PermissionError):
                        continue
            except Exception as e:
                print(f"Could not check daemon status: {e}")
            
            if daemon_running:
                print("Daemon is already running - settings will be updated automatically via GSettings")
                return True
            
            # Start daemon using GLib spawn
            from gi.repository import GLib
            
            print("Starting daemon...")
            success, pid = GLib.spawn_async(
                argv=['pardus-gnome-greeter', '--daemon'],
                flags=GLib.SpawnFlags.SEARCH_PATH | GLib.SpawnFlags.STDOUT_TO_DEV_NULL | GLib.SpawnFlags.STDERR_TO_DEV_NULL,
                envp=None,
                working_directory=None,
                child_setup=None,
                user_data=None
            )
            
            if success:
                print(f"Daemon started successfully (PID: {pid})")
                return True
            else:
                print("Failed to start daemon")
                return False
            
        except Exception as e:
            print(f"Error starting daemon: {e}")
            return False
    
    def stop_background_service(self):
        """Stop background daemon service
        
        Note: We don't actually stop the daemon, just disable it via GSettings.
        The daemon will stop its timers but remain running (minimal resource usage).
        This avoids subprocess calls and the daemon can quickly resume when re-enabled.
        """
        # Settings are already updated (live-wallpaper-enabled = False)
        # Daemon will receive the signal via GSettings and stop its timers
        print("Daemon will stop its timers via GSettings (live-wallpaper-enabled = False)")
        return True