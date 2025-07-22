from pydbus import SessionBus
from gi.repository import GLib
import threading

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
            serial, crtcs, outputs, modes = result[:4]

            modes_by_id = {mode[0]: mode for mode in modes}

            active_mode_ids = {}
            for crtc in crtcs:
                if len(crtc) >= 6 and crtc[5] != 0: # mode_id 0 means disabled
                    active_mode_ids[crtc[0]] = crtc[5]

            for i, output in enumerate(outputs):
                if len(output) < 8: continue
                
                output_id, _, current_crtc_id, _, _, _, _, properties = output
                if not isinstance(properties, dict): continue

                display_name = properties.get('display-name', f"Monitor {i+1}")

                monitor_data = {
                    'id': output_id,
                    'name': display_name,
                    'scale': 1.0,
                    'supported_scales': [1.0]
                }
                
                if current_crtc_id in active_mode_ids:
                    mode_id = active_mode_ids[current_crtc_id]
                    if mode_id in modes_by_id:
                        # mode: (id, w, h, refresh, scale, supported_scales, props)
                        mode_data = modes_by_id[mode_id]
                        if len(mode_data) >= 6:
                            monitor_data['scale'] = mode_data[4]
                            supported = mode_data[5]
                            if supported:
                                monitor_data['supported_scales'] = supported
                
                config.append(monitor_data)
        
        except Exception as e:
            print(f"DisplayManager Error: Failed to get monitor info via D-Bus. {e}")
            config = [] # Clear config on error to avoid partial data

        self._finish_loading(config)

    def _finish_loading(self, config):
        self._monitors_config = config
        for cb in self._callbacks:
            GLib.idle_add(cb, config)
        self._callbacks = []

display_manager = DisplayManager()