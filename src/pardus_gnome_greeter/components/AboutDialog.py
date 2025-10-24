import gi
import os
import re

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

def create_about_dialog(parent=None):
    dialog = Adw.AboutDialog.new()
    dialog.set_application_name(_('Pardus GNOME Greeter'))
    dialog.set_version(_get_version())
    dialog.set_developer_name('Osman Coskun')
    dialog.set_license_type(Gtk.License.LGPL_3_0)
    dialog.set_comments(
        _('Customize and configure Pardus with few clicks')
    )
    dialog.set_website('https://github.com/pardus/pardus-gnome-greeter')
    dialog.set_issue_url('https://github.com/pardus/pardus-gnome-greeter/issues')
    dialog.set_translator_credits(_('Osman Coskun <osman.coskun@pardus.org.tr>'))
    dialog.set_copyright(_('© 2025 Pardus Team'))
    dialog.set_developers([_('Osman Coskun <osman.coskun@pardus.org.tr>'),_('Fatih Altun <fatih.altun@pardus.org.tr>')])
    return dialog

def _get_version():
    """Get version from meson.build or fallback to default"""
    try:
        # Try to read from meson.build
        meson_build_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'meson.build')
        if os.path.exists(meson_build_path):
            with open(meson_build_path, 'r') as f:
                content = f.read()
                # Look for version: '0.0.13'
                match = re.search(r"version:\s*'([^']+)'", content)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"Error reading version: {e}")
    
    # Fallback version
    return "0.0.13"
