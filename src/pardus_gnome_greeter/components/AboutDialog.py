import gi
import os
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
    dialog.set_translator_credits(_('Hugo Carvalho <hugokarvalho@hotmail.com>'))
    dialog.set_copyright(_('© 2025 Pardus Team'))
    dialog.set_developers([_('Osman Coskun <osman.coskun@pardus.org.tr>'), ('Fatih Altun <fatih.altun@pardus.org.tr>')])
    return dialog

def _get_version():
    """Get version from meson.build or fallback to default"""
    try:
        version = open(os.path.dirname(os.path.abspath(__file__)) + "/../../__version__").readline().strip()
        return version
    except Exception as e:
        print(f"Error reading version: {e}")
        return "0.0.13"
