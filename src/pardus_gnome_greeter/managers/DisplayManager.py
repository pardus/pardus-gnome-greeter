from pydbus import SessionBus
from gi.repository import GLib
import threading
try:
    import dbus
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False
    print("Warning: python-dbus not available, resolution changing will not work")

class DisplayManager:
    def __init__(self):
        self._monitors_config = None
        self._callbacks = []
        self._loading_thread = None

    def get_monitors(self, callback):
        if self._monitors_config is not None:
            GLib.idle_add(callback, self._monitors_config)
            return
        
        self._callbacks.append(callback)
        
        if self._loading_thread is None or not self._loading_thread.is_alive():
            self._loading_thread = threading.Thread(target=self._fetch_monitor_resources)
            self._loading_thread.start()

    def _fetch_monitor_resources(self):
        config = []
        try:
            bus = SessionBus()
            proxy = bus.get("org.gnome.Mutter.DisplayConfig", "/org/gnome/Mutter/DisplayConfig")
            
            # GetResources returns: (serial, crtcs, outputs, modes, max_w, max_h)
            result = proxy.GetResources()
            print("DisplayManager: Raw D-Bus response received")
            serial, crtcs, outputs, modes = result[:4]

            modes_by_id = {mode[0]: mode for mode in modes}
            
            print(f"DEBUG: First few modes: {modes[:3]}")
            print(f"DEBUG: modes_by_id keys: {list(modes_by_id.keys())[:10]}")

            active_mode_ids = {}
            for crtc in crtcs:
                if len(crtc) >= 6 and crtc[5] != 0: # mode_id 0 means disabled
                    active_mode_ids[crtc[0]] = crtc[5]
            
            print(f"DEBUG: Active mode IDs: {active_mode_ids}")
            
            # Create a mapping from active mode ID to actual mode data by searching height
            active_mode_data = {}
            for crtc_id, active_mode_id in active_mode_ids.items():
                # Try to find mode by height (seems like mode ID correlates with height)
                for mode in modes:
                    if len(mode) >= 4 and mode[3] == active_mode_id:  # mode[3] is height
                        active_mode_data[crtc_id] = mode
                        print(f"DEBUG: Matched CRTC {crtc_id} with mode: {mode}")
                        break

            for i, output in enumerate(outputs):
                if len(output) < 8: continue
                
                output_id, _, current_crtc_id, possible_crtcs, output_name, available_mode_ids, _, properties = output
                if not isinstance(properties, dict): continue

                # Extract vendor and product information for meaningful display names
                vendor = properties.get('vendor', '')
                product = properties.get('product', '')
                display_name = properties.get('display-name', f"Monitor {i+1}")
                
                # Create a meaningful monitor name using vendor and product
                if vendor and product:
                    # Handle common vendor codes
                    vendor_names = {
                        'SAM': 'Samsung',
                        'LEN': 'Lenovo',
                        'DEL': 'Dell',
                        'ACI': 'ASUS',
                        'AOC': 'AOC',
                        'BNQ': 'BenQ',
                        'HPN': 'HP',
                        'LGD': 'LG',
                        'ACR': 'Acer',
                        'VSC': 'ViewSonic'
                    }
                    
                    full_vendor_name = vendor_names.get(vendor, vendor)
                    
                    # Clean up product name (remove vendor prefix if it exists in product name)
                    clean_product = product
                    if product.upper().startswith(vendor.upper()):
                        clean_product = product[len(vendor):].strip()
                    
                    monitor_name = f"{full_vendor_name} {clean_product}"
                else:
                    # Fallback to connection type if vendor/product not available
                    monitor_name = display_name

                # Extract resolution information
                current_resolution = None
                supported_resolutions = []
                current_scale = 1.0  # Default scale
                
                # Get available resolutions for this output
                if isinstance(available_mode_ids, list):
                    for mode_id in available_mode_ids:
                        if mode_id in modes_by_id:
                            mode_data = modes_by_id[mode_id]
                            if len(mode_data) >= 4:
                                width = mode_data[2]
                                height = mode_data[3]
                                refresh_rate = mode_data[4] if len(mode_data) > 4 else 60.0
                                supported_scales_for_mode = mode_data[6] if len(mode_data) > 6 else [1.0]
                                
                                resolution_str = f"{width}x{height}"
                                if resolution_str not in [res['resolution'] for res in supported_resolutions]:
                                    supported_resolutions.append({
                                        'resolution': resolution_str,
                                        'width': width,
                                        'height': height,
                                        'refresh_rate': refresh_rate,
                                        'mode_id': mode_id,
                                        'supported_scales': supported_scales_for_mode
                                    })

                monitor_data = {
                    'id': output_id,
                    'name': monitor_name,
                    'connection_type': display_name,  # Keep original connection info
                    'vendor': vendor,
                    'product': product,
                    'scale': current_scale,
                    'supported_scales': [1.0],
                    'current_resolution': current_resolution,
                    'supported_resolutions': supported_resolutions,
                    'connector': output_name  # Add connector for resolution changing
                }
                
                print(f"DEBUG: Monitor {output_id} - current_crtc_id: {current_crtc_id}")
                print(f"DEBUG: Active mode IDs: {active_mode_ids}")
                
                if current_crtc_id in active_mode_data:
                    mode_data = active_mode_data[current_crtc_id]
                    print(f"DEBUG: Found active mode_data: {mode_data}")
                    
                    if len(mode_data) >= 4:
                        # Set current resolution
                        width = mode_data[2]
                        height = mode_data[3] 
                        refresh_rate = mode_data[4] if len(mode_data) > 4 else 60.0
                        mode_id = mode_data[0]  # Use the actual mode ID from the mode data
                        
                        monitor_data['current_resolution'] = {
                            'resolution': f"{width}x{height}",
                            'width': width,
                            'height': height,
                            'refresh_rate': refresh_rate,
                            'mode_id': mode_id
                        }
                        
                        print(f"  Set current resolution: {width}x{height} @ {refresh_rate:.1f}Hz (mode_id: {mode_id})")
                    
                    # Get current scale - note: GetResources modes may not have scale info
                    # We'll use GetCurrentState for accurate scale data later
                    if len(mode_data) >= 6:
                        supported = mode_data[6] if len(mode_data) > 6 else [1.0]
                        if supported and len(supported) > 1:
                            monitor_data['supported_scales'] = supported
                            print(f"  Found supported scales: {supported}")
                        else:
                            print(f"  No scale data in GetResources mode, will use GetCurrentState")
                else:
                    print(f"DEBUG: current_crtc_id {current_crtc_id} not in active_mode_data")
                
                # Update current resolution in supported_resolutions with actual current scale info
                if monitor_data['current_resolution']:
                    current_res_str = monitor_data['current_resolution']['resolution']
                    current_refresh = monitor_data['current_resolution']['refresh_rate']
                    
                    # Find the matching resolution in supported_resolutions and update its scale info
                    for res_info in monitor_data['supported_resolutions']:
                        if (res_info['resolution'] == current_res_str and 
                            abs(res_info['refresh_rate'] - current_refresh) < 0.1):
                            # Update this resolution with current scale information
                            if 'supported_scales' not in res_info or not res_info['supported_scales']:
                                res_info['supported_scales'] = monitor_data['supported_scales']
                            print(f"  Updated resolution {current_res_str} with scales: {res_info['supported_scales']}")
                            break
                
                # Try to get actual scale information from GetCurrentState
                try:
                    # Import here to avoid circular import
                    import dbus
                    bus = dbus.SessionBus()
                    display_config_proxy = bus.get_object("org.gnome.Mutter.DisplayConfig", "/org/gnome/Mutter/DisplayConfig")
                    display_config_interface = dbus.Interface(display_config_proxy, dbus_interface="org.gnome.Mutter.DisplayConfig")
                    
                    # Get current state for scale information
                    serial, physical_monitors, logical_monitors, properties = display_config_interface.GetCurrentState()
                    
                    # Find our monitor in the current state by connector name
                    for monitor_info_current, monitor_modes_current, monitor_properties_current in physical_monitors:
                        connector_name = str(monitor_info_current[0])
                        if connector_name == output_name:
                            # Found our monitor, get current mode scale info
                            for mode_string, mode_width, mode_height, mode_refresh, mode_preferred_scale, mode_supported_scales, mode_properties in monitor_modes_current:
                                if mode_properties.get("is-current", False):
                                    # This is the current mode, get its scale info
                                    current_scale_actual = float(mode_preferred_scale) if mode_preferred_scale else 1.0
                                    supported_scales_actual = [float(s) for s in mode_supported_scales] if mode_supported_scales else [1.0]
                                    
                                    # Also check logical monitors for actual scale
                                    for x, y, scale, transform, primary, linked_monitors_info, props in logical_monitors:
                                        for linked_monitor_connector, linked_monitor_vendor, linked_monitor_product, linked_monitor_serial in linked_monitors_info:
                                            if linked_monitor_connector == connector_name:
                                                # Use logical monitor scale if available
                                                current_scale_actual = float(scale)
                                                print(f"  Found logical monitor scale: {current_scale_actual}")
                                                break
                                        if current_scale_actual != 1.0:
                                            break
                                    
                                    monitor_data['scale'] = current_scale_actual
                                    monitor_data['supported_scales'] = supported_scales_actual
                                    
                                    # Update current_scale variable for filtering
                                    current_scale = current_scale_actual
                                    
                                    print(f"  GetCurrentState: scale={current_scale_actual}, supported_scales={supported_scales_actual}")
                                    
                                    # Update current resolution in supported_resolutions with GetCurrentState scale data
                                    if monitor_data['current_resolution']:
                                        current_res_str = monitor_data['current_resolution']['resolution']
                                        for res_info in monitor_data['supported_resolutions']:
                                            if res_info['resolution'] == current_res_str:
                                                res_info['supported_scales'] = supported_scales_actual
                                                print(f"  Updated {current_res_str} with GetCurrentState scales: {supported_scales_actual}")
                                                break
                                    break
                            break
                except Exception as e:
                    print(f"  Warning: Could not get scale info from GetCurrentState: {e}")
                
                # Filter supported resolutions based on current scale
                if current_scale != 1.0:
                    # If current scale is not 1.0, only show resolutions that support this scale
                    filtered_resolutions = []
                    for res in supported_resolutions:
                        if current_scale in res['supported_scales']:
                            filtered_resolutions.append(res)
                    
                    # If no resolutions support the current scale, show all resolutions
                    # This prevents the dropdown from being empty
                    if len(filtered_resolutions) == 0:
                        print(f"  No resolutions support scale {current_scale}, showing all {len(supported_resolutions)} resolutions")
                        monitor_data['supported_resolutions'] = supported_resolutions
                    else:
                        monitor_data['supported_resolutions'] = filtered_resolutions
                        print(f"  Filtered to {len(filtered_resolutions)} resolutions supporting scale {current_scale}")
                else:
                    print(f"  Scale is 1.0, showing all {len(supported_resolutions)} resolutions")
                
                config.append(monitor_data)
                current_res_str = monitor_data['current_resolution']['resolution'] if monitor_data['current_resolution'] else "Unknown"
                supported_res_count = len(monitor_data['supported_resolutions'])
                print(f"DisplayManager: Found monitor - {monitor_name} (Vendor: {vendor}, Product: {product}, Connection: {display_name})")
                print(f"  Current Resolution: {current_res_str}, Supported Resolutions: {supported_res_count}")
        
        except Exception as e:
            print(f"DisplayManager Error: Failed to get monitor info via D-Bus. {e}")
            config = [] # Clear config on error to avoid partial data

        self._finish_loading(config)

    def _finish_loading(self, config):
        self._monitors_config = config
        for cb in self._callbacks:
            GLib.idle_add(cb, config)
        self._callbacks = []

    def apply_resolution_change(self, monitor_id, mode_id):
        """Apply resolution change using proper dbus module like the example script"""
        if not DBUS_AVAILABLE:
            print("Error: python-dbus not available for resolution changing")
            return False
            
        try:
            # Use standard dbus module like the working script
            bus = dbus.SessionBus()
            
            display_config_well_known_name = "org.gnome.Mutter.DisplayConfig"
            display_config_object_path = "/org/gnome/Mutter/DisplayConfig"
            
            display_config_proxy = bus.get_object(display_config_well_known_name, display_config_object_path)
            display_config_interface = dbus.Interface(display_config_proxy, dbus_interface=display_config_well_known_name)
            
            # First get resources to find the mode details
            result = display_config_interface.GetResources()
            serial_res, crtcs, outputs, modes = result[:4]
            
            # Find the target mode width/height from GetResources
            target_width = None
            target_height = None
            for mode in modes:
                if mode[0] == mode_id:  # mode[0] is the integer mode ID
                    target_width = mode[2]
                    target_height = mode[3]
                    break
            
            if target_width is None or target_height is None:
                print(f"Mode {mode_id} not found in resources")
                return False
            
            print(f"Looking for mode with resolution {target_width}x{target_height}")
            
            # Get current state
            serial, physical_monitors, logical_monitors, properties = display_config_interface.GetCurrentState()
            
            # Find the exact mode string from GetCurrentState physical monitors
            target_mode_string = None
            target_supported_scales = None
            for monitor_info, monitor_modes, monitor_properties in physical_monitors:
                for mode_string, mode_width, mode_height, mode_refresh, mode_preferred_scale, mode_supported_scales, mode_properties in monitor_modes:
                    if mode_width == target_width and mode_height == target_height:
                        target_mode_string = mode_string
                        target_supported_scales = list(mode_supported_scales)
                        print(f"Found matching mode string: {target_mode_string}")
                        print(f"Supported scales for this mode: {target_supported_scales}")
                        break
                if target_mode_string:
                    break
            
            if not target_mode_string:
                print(f"Could not find mode string for resolution {target_width}x{target_height}")
                return False
            
            print(f"Changing resolution for monitor {monitor_id} to mode {target_mode_string}")
            
            # Find our monitor info
            target_monitor = None
            for monitor_data in self._monitors_config:
                if monitor_data['id'] == monitor_id:
                    target_monitor = monitor_data
                    break
                    
            if not target_monitor:
                print(f"Monitor {monitor_id} not found in config")
                return False
            
            target_connector = target_monitor['connector']
            print(f"Target connector: {target_connector}")
            
            updated_logical_monitors = []
            monitor_found = False
            
            # Collect information about all monitors and their new configurations
            monitor_configs = []
            
            for x, y, scale, transform, primary, linked_monitors_info, props in logical_monitors:
                physical_monitors_config = []
                current_logical_monitor_has_target = False
                monitor_width = 1920  # Default width, will be updated
                
                for linked_monitor_connector, linked_monitor_vendor, linked_monitor_product, linked_monitor_serial in linked_monitors_info:
                    for monitor_info, monitor_modes, monitor_properties in physical_monitors:
                        monitor_connector, monitor_vendor, monitor_product, monitor_serial = monitor_info
                        
                        if linked_monitor_connector == monitor_connector:
                            if monitor_connector == target_connector:
                                # This is our target monitor - use the new mode (as string)
                                physical_monitors_config.append(dbus.Struct([monitor_connector, target_mode_string, {}]))
                                monitor_found = True
                                current_logical_monitor_has_target = True
                                monitor_width = target_width  # Use new width
                                print(f"Found target monitor {monitor_connector}, setting mode to {target_mode_string}")
                            else:
                                # Keep current mode for other monitors - find current mode ID properly
                                current_mode_string = None
                                current_mode_width = 1920  # Default
                                
                                for mode_string, mode_width, mode_height, mode_refresh, mode_preferred_scale, mode_supported_scales, mode_properties in monitor_modes:
                                    if mode_properties.get("is-current", False):
                                        current_mode_string = mode_string
                                        current_mode_width = mode_width
                                        break
                                
                                if current_mode_string is not None:
                                    physical_monitors_config.append(dbus.Struct([monitor_connector, current_mode_string, {}]))
                                    monitor_width = current_mode_width
                                    print(f"Keeping current mode {current_mode_string} for monitor {monitor_connector}")
                                else:
                                    print(f"Warning: Could not find current mode for monitor {monitor_connector}")
                
                # Store monitor configuration
                monitor_configs.append({
                    'physical_monitors_config': physical_monitors_config,
                    'width': monitor_width,
                    'scale': 1.0 if current_logical_monitor_has_target else scale,
                    'transform': transform,
                    'primary': primary,
                    'is_target': current_logical_monitor_has_target
                })
            
            if not monitor_found:
                print(f"Target monitor connector {target_connector} not found")
                return False
            
            # Recalculate positions - arrange all monitors horizontally from left to right
            current_x = 0
            for i, monitor_config in enumerate(monitor_configs):
                new_x = current_x
                new_y = 0  # All monitors at same vertical level
                
                # Create logical monitor struct with calculated position
                updated_logical_monitor_struct = dbus.Struct([
                    dbus.Int32(new_x),
                    dbus.Int32(new_y),
                    dbus.Double(monitor_config['scale']),
                    dbus.UInt32(monitor_config['transform']), 
                    dbus.Boolean(monitor_config['primary']), 
                    monitor_config['physical_monitors_config']
                ])
                updated_logical_monitors.append(updated_logical_monitor_struct)
                
                print(f"Monitor {i}: position ({new_x}, {new_y}), width {monitor_config['width']}, target: {monitor_config['is_target']}")
                
                # Next monitor starts after this one
                current_x += monitor_config['width']
            
            print(f"Final configuration: {len(updated_logical_monitors)} logical monitors arranged horizontally")
            
            # Apply the configuration
            properties_to_apply = {"layout-mode": properties.get("layout-mode")}
            method = 2  # Show confirmation dialog
            
            display_config_interface.ApplyMonitorsConfig(
                dbus.UInt32(serial), 
                dbus.UInt32(method), 
                updated_logical_monitors, 
                properties_to_apply
            )
            
            print(f"Successfully applied resolution change for monitor {monitor_id}")
            
            # Refresh our monitor data after change
            GLib.timeout_add(1000, self._delayed_refresh)
            
            return True
            
        except Exception as e:
            print(f"Error applying resolution change: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def apply_scale_change(self, monitor_id, mode_id, new_scale):
        """Apply scale change to a specific monitor"""
        try:
            if not self._monitors_config:
                print("No monitor configuration available")
                return False
            
            # Find target monitor
            target_connector = None
            for monitor in self._monitors_config:
                if monitor['id'] == monitor_id:
                    target_connector = monitor['connector']
                    break
            
            if not target_connector:
                print(f"Monitor {monitor_id} not found")
                return False
            
            print(f"Changing scale for monitor {monitor_id} to {new_scale}")
            print(f"Target connector: {target_connector}")
            
            # Get current state from D-Bus
            bus = dbus.SessionBus()
            display_config_well_known_name = "org.gnome.Mutter.DisplayConfig"
            display_config_object_path = "/org/gnome/Mutter/DisplayConfig"
            
            display_config_proxy = bus.get_object(display_config_well_known_name, display_config_object_path)
            display_config_interface = dbus.Interface(display_config_proxy, dbus_interface=display_config_well_known_name)
            
            # Get current state
            current_state = display_config_interface.GetCurrentState()
            serial = current_state[0]
            physical_monitors = current_state[1]
            logical_monitors = current_state[2]
            properties = current_state[3]
            
            print(f"Current state: {len(physical_monitors)} physical monitors, {len(logical_monitors)} logical monitors")
            
            # Process logical monitors and normalize coordinates
            updated_logical_monitors = []
            monitor_found = False
            
            # First pass: find all logical monitors and their positions
            logical_monitor_positions = []
            for x, y, scale, transform, primary, linked_monitors_info, props in logical_monitors:
                logical_monitor_positions.append((x, y, scale, transform, primary, linked_monitors_info, props))
            
            # Arrange all monitors strictly side by side, y=0 for all
            if logical_monitor_positions:
                # Calculate actual monitor widths for each logical monitor
                monitor_widths = []
                for x, y, scale, transform, primary, linked_monitors_info, props in logical_monitor_positions:
                    width = None
                    is_target = False
                    for linked_monitor_connector, linked_monitor_vendor, linked_monitor_product, linked_monitor_serial in linked_monitors_info:
                        for monitor_info, monitor_modes, monitor_properties in physical_monitors:
                            monitor_connector, monitor_vendor, monitor_product, monitor_serial = monitor_info
                            if linked_monitor_connector == monitor_connector:
                                # Target monitör ise yeni scale ile hesapla
                                if monitor_connector == target_connector:
                                    is_target = True
                                for mode_string, mode_width, mode_height, mode_refresh, mode_preferred_scale, mode_supported_scales, mode_properties in monitor_modes:
                                    if mode_properties.get("is-current", False):
                                        if is_target:
                                            width = int(mode_width / new_scale)
                                        else:
                                            width = int(mode_width / scale)
                                        break
                        if width is not None:
                            break
                    if width is None:
                        width = 1920  # fallback
                    monitor_widths.append(width)

                # Now arrange
                arranged_positions = []
                current_x = 0
                for i, (orig, width) in enumerate(zip(logical_monitor_positions, monitor_widths)):
                    x, y, scale, transform, primary, linked_monitors_info, props = orig
                    new_x = current_x
                    new_y = 0
                    arranged_positions.append((new_x, new_y, scale, transform, primary, linked_monitors_info, props))
                    current_x += width
                logical_monitor_positions = arranged_positions
                print(f"All monitors arranged strictly side by side, y=0, with calculated widths (target uses new scale)")
            
            # Second pass: build updated logical monitors
            for x, y, scale, transform, primary, linked_monitors_info, props in logical_monitor_positions:
                physical_monitors_config = []
                current_logical_monitor_has_target = False
                
                for linked_monitor_connector, linked_monitor_vendor, linked_monitor_product, linked_monitor_serial in linked_monitors_info:
                    for monitor_info, monitor_modes, monitor_properties in physical_monitors:
                        monitor_connector, monitor_vendor, monitor_product, monitor_serial = monitor_info
                        
                        if linked_monitor_connector == monitor_connector:
                            if monitor_connector == target_connector:
                                # This is our target monitor - keep current mode but change scale
                                current_mode_string = None
                                for mode_string, mode_width, mode_height, mode_refresh, mode_preferred_scale, mode_supported_scales, mode_properties in monitor_modes:
                                    if mode_properties.get("is-current", False):
                                        current_mode_string = mode_string
                                        break
                                        
                                if current_mode_string:
                                    physical_monitors_config.append(dbus.Struct([monitor_connector, current_mode_string, {}]))
                                    monitor_found = True
                                    current_logical_monitor_has_target = True
                                    print(f"Found target monitor {monitor_connector}, keeping mode {current_mode_string}, changing scale to {new_scale}")
                                else:
                                    print(f"Error: Could not find current mode for target monitor {monitor_connector}")
                                    return False
                            else:
                                # Keep current mode for other monitors
                                current_mode_string = None
                                for mode_string, mode_width, mode_height, mode_refresh, mode_preferred_scale, mode_supported_scales, mode_properties in monitor_modes:
                                    if mode_properties.get("is-current", False):
                                        current_mode_string = mode_string
                                        break
                                
                                if current_mode_string is not None:
                                    physical_monitors_config.append(dbus.Struct([monitor_connector, current_mode_string, {}]))
                                    print(f"Keeping current mode {current_mode_string} for monitor {monitor_connector}")
                                else:
                                    print(f"Warning: Could not find current mode for monitor {monitor_connector}")
                
                # Use new scale for target monitor, keep original for others
                if current_logical_monitor_has_target:
                    use_scale = new_scale
                    print(f"Setting scale to {new_scale} for target monitor")
                else:
                    use_scale = scale  # Keep original scale for other monitors
                
                # Create updated logical monitor struct with normalized coordinates
                updated_logical_monitor_struct = dbus.Struct([
                    dbus.Int32(x),  # Use normalized position
                    dbus.Int32(y),  # Use normalized position
                    dbus.Double(use_scale),
                    dbus.UInt32(transform), 
                    dbus.Boolean(primary), 
                    physical_monitors_config
                ])
                updated_logical_monitors.append(updated_logical_monitor_struct)
                
                print(f"Logical monitor: position ({x}, {y}), scale {use_scale}, target: {current_logical_monitor_has_target}")
            
            if not monitor_found:
                print(f"Target monitor connector {target_connector} not found")
                return False
            
            print(f"Final configuration: {len(updated_logical_monitors)} logical monitors with scale change")
            
            # Apply the configuration
            properties_to_apply = {"layout-mode": properties.get("layout-mode")}
            method = 2  # Show confirmation dialog
            
            display_config_interface.ApplyMonitorsConfig(
                dbus.UInt32(serial), 
                dbus.UInt32(method), 
                updated_logical_monitors, 
                properties_to_apply
            )
            
            print(f"Successfully applied scale change for monitor {monitor_id}")
            
            # Refresh our monitor data after change
            GLib.timeout_add(1000, self._delayed_refresh)
            
            return True
            
        except Exception as e:
            print(f"Error applying scale change: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _delayed_refresh(self):
        """Delayed refresh of monitor configuration"""
        self._monitors_config = None
        self._fetch_monitor_resources()
        return False  # Don't repeat the timeout

display_manager = DisplayManager()