#!/usr/bin/env python3
"""
Pardus GNOME Greeter Daemon
Background service for automatic wallpaper downloading and rotation
"""

import gi
import sys
import signal
from datetime import datetime, timedelta

gi.require_version('GLib', '2.0')
gi.require_version('Gio', '2.0')
from gi.repository import GLib, Gio

from pardus_gnome_greeter.managers.LiveWallpaperManager import LiveWallpaperManager
from pardus_gnome_greeter.managers.settings import app_settings


class GreeterDaemon:
    """Background daemon for wallpaper management"""
    
    def __init__(self):
        self.manager = LiveWallpaperManager()
        self.loop = GLib.MainLoop()
        self.shuffle_timeout_id = None
        self.last_check_date = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.on_signal)
        signal.signal(signal.SIGTERM, self.on_signal)
        
        # Listen to settings changes
        self.setup_settings_listener()
        
        print("Pardus GNOME Greeter Daemon started")
    
    def setup_settings_listener(self):
        """Setup GSettings listener for configuration changes"""
        try:
            # Connect to settings changes
            app_settings.settings.connect('changed::live-wallpaper-enabled', self.on_enabled_changed)
            app_settings.settings.connect('changed::live-wallpaper-shuffle-interval', self.on_shuffle_interval_changed)
            app_settings.settings.connect('changed::live-wallpaper-sources', self.on_sources_changed)
        except Exception as e:
            print(f"Warning: Could not setup settings listener: {e}")
    
    def on_signal(self, signum, frame):
        """Handle termination signals"""
        print(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def on_enabled_changed(self, settings, key):
        """Handle live wallpaper enabled/disabled"""
        enabled = self.manager.is_enabled()
        print(f"Live wallpaper {'enabled' if enabled else 'disabled'}")
        
        if enabled:
            # Check and download immediately
            self.check_daily_wallpapers()
            # Schedule shuffling
            self.schedule_shuffle()
        else:
            # Stop shuffling
            if self.shuffle_timeout_id:
                GLib.source_remove(self.shuffle_timeout_id)
                self.shuffle_timeout_id = None
    
    def on_shuffle_interval_changed(self, settings, key):
        """Handle shuffle interval change"""
        interval = self.manager.get_shuffle_interval()
        print(f"Shuffle interval changed to {interval} minutes")
        
        # Re-schedule shuffle with new interval
        self.schedule_shuffle()
    
    def on_sources_changed(self, settings, key):
        """Handle selected sources change"""
        sources = self.manager.get_selected_sources()
        print(f"Selected sources changed: {sources}")
        
        # Reset source index when sources change
        self.manager.set_current_source_index(0)
    
    def start(self):
        """Start the daemon"""
        # Check if live wallpaper is enabled
        if not self.manager.is_enabled():
            print("Live wallpaper is disabled, daemon will not run")
            return
        
        # Initial daily check
        self.check_daily_wallpapers()
        
        # Schedule wallpaper shuffling (which also checks for day changes)
        self.schedule_shuffle()
        
        # Run main loop
        try:
            self.loop.run()
        except KeyboardInterrupt:
            self.stop()
    
    def check_daily_wallpapers(self):
        """Check and download today's wallpapers if not already downloaded"""
        try:
            if not self.manager.is_enabled():
                return
            
            # Check if we need to download today's wallpapers
            if self.manager.should_check_daily_wallpapers():
                print("Downloading today's wallpapers...")
                
                selected_sources = self.manager.get_selected_sources()
                if not selected_sources:
                    print("No sources selected")
                    return
                
                # Download from each selected source
                for source_id in selected_sources:
                    print(f"Downloading from {source_id}...")
                    result = self.manager.download_wallpaper_from_source(source_id)
                    
                    if result and result.get('status') == 'available':
                        print(f"✓ Downloaded: {result.get('title')}")
                    elif result and result.get('status') == 'error':
                        print(f"✗ Error: {result.get('error_message')}")
                
                # Mark today as checked
                self.manager.set_last_check_date()
                self.last_check_date = datetime.now().date()
                print("Daily wallpaper check completed")
            else:
                print("Today's wallpapers already downloaded")
                self.last_check_date = datetime.now().date()
        
        except Exception as e:
            print(f"Error during daily check: {e}")
    
    def schedule_shuffle(self):
        """Schedule automatic wallpaper shuffling"""
        # Cancel existing timeout
        if self.shuffle_timeout_id:
            GLib.source_remove(self.shuffle_timeout_id)
            self.shuffle_timeout_id = None
        
        if not self.manager.is_enabled():
            return
        
        # Get shuffle interval (in minutes)
        shuffle_interval = self.manager.get_shuffle_interval()
        
        if shuffle_interval <= 0:
            print("Wallpaper shuffle is disabled")
            return
        
        # Convert to milliseconds
        interval_ms = shuffle_interval * 60 * 1000
        
        print(f"Scheduling wallpaper shuffle every {shuffle_interval} minutes")
        
        # Schedule shuffle
        self.shuffle_timeout_id = GLib.timeout_add(interval_ms, self.cycle_wallpaper)
    
    def cycle_wallpaper(self):
        """Cycle to next wallpaper source and check for day change"""
        try:
            if not self.manager.is_enabled():
                return True
            
            # Check if day has changed
            current_date = datetime.now().date()
            if self.last_check_date and current_date > self.last_check_date:
                print(f"Day changed from {self.last_check_date} to {current_date}")
                self.check_daily_wallpapers()
            
            print("Cycling wallpaper...")
            
            selected_sources = self.manager.get_selected_sources()
            if not selected_sources:
                print("No sources selected")
                return True
            
            # Get current source index
            current_index = self.manager.get_current_source_index()
            
            # Move to next source (cycle through)
            next_index = (current_index + 1) % len(selected_sources)
            source_id = selected_sources[next_index]
            
            # Load metadata for this source (from today's cache)
            wallpaper_data = self.manager.load_metadata(source_id)
            
            if wallpaper_data and wallpaper_data.filepath:
                # Apply wallpaper using WallpaperManager
                from pardus_gnome_greeter.managers.WallpaperManager import WallpaperManager
                wallpaper_manager = WallpaperManager()
                wallpaper_manager.change_wallpaper(wallpaper_data.filepath)
                
                print(f"✓ Applied wallpaper from {source_id}: {wallpaper_data.title}")
                
                # Update current source index
                self.manager.set_current_source_index(next_index)
            else:
                print(f"✗ No wallpaper available from {source_id}")
        
        except Exception as e:
            print(f"Error during wallpaper cycle: {e}")
        
        return True  # Continue timeout
    
    def stop(self):
        """Stop the daemon"""
        print("Stopping daemon...")
        
        # Remove timeout
        if self.shuffle_timeout_id:
            GLib.source_remove(self.shuffle_timeout_id)
        
        # Quit main loop
        self.loop.quit()


def main():
    """Main entry point"""
    daemon = GreeterDaemon()
    daemon.start()
    return 0


if __name__ == '__main__':
    sys.exit(main())
