import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gtk
from .Widget import Widget

licences = {
    "unknown": Gtk.License(0),
    "custom": Gtk.License(1),
    "GPL-2": Gtk.License(2),
    "GPL-3": Gtk.License(3),
    "LGPL-2-1": Gtk.License(4),
    "LGPL-3-0": Gtk.License(5),
    "BSD": Gtk.License(6),
    "MIX-X11": Gtk.License(7),
    "ARTISTIC": Gtk.License(8),
    "GPL-2-0-ONLY": Gtk.License(9),
    "GPL-3-0-ONLY": Gtk.License(10),
    "LGPL-2-1-ONLY": Gtk.License(11),
    "LGPL-3-0-ONLY": Gtk.License(12),
    "AGPL-3-0": Gtk.License(13),
    "AGPL-3-0-ONLY": Gtk.License(14),
    "BSD-3": Gtk.License(15),
    "APACHE-2-0": Gtk.License(16),
    "MPL-2-0": Gtk.License(17),
}


class AboutWindow(Widget):
    def __init__(
        self,
        *args,
        application_name=None,
        version=None,
        developer_name=None,
        license_type=None,
        comments=None,
        website=None,
        issue_url=None,
        credit_section=None,
        translator_credits=None,
        copyright=None,
        developers=None,
        application_icon=None,
        transient_for=None,
        modal=False,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self = Adw.AboutWindow()
        self.set_application_name(application_name)
        self.set_version(version)
        self.set_developer_name(developer_name)
        self.set_license_type(licences[license_type])
        self.set_comments(comments)
        self.set_website(website)
        self.set_issue_url(issue_url)
        self.add_credit_section(credit_section[0], credit_section[1])
        self.set_translator_credits(translator_credits)
        self.set_copyright(copyright)
        self.set_developers(developers)
        self.set_application_icon(application_icon)
        self.set_transient_for(transient_for)
        self.set_modal(modal)
        self.show()
