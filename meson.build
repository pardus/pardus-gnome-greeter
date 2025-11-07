project('pardus-gnome-greeter', 'c',
    version: '0.0.13',
    meson_version: '>= 0.60.0'
)

application_id = 'tr.org.pardus.pardus-gnome-greeter'
project_name = meson.project_name()
prefix = get_option('prefix')
datadir = join_paths(prefix, get_option('datadir'))
pkgdatadir = join_paths(datadir, project_name)

# GResource
gnome = import('gnome')
gresource_target = custom_target(
    'pardus-gnome-greeter-gresource',
    input: 'pardus-gnome-greeter.gresource.xml',
    output: 'pardus-gnome-greeter.gresource',
    command: [
        'glib-compile-resources',
        '--target=@OUTPUT@',
        '--sourcedir=' + meson.current_source_dir() + '/data',
        '@INPUT@'
    ],
    install: true,
    install_dir: pkgdatadir
)

# Python sources - Install to pkgdatadir for application use
install_subdir(
    'src/pardus_gnome_greeter',
    install_dir: pkgdatadir
)

# Python package - Install to dist-packages for library use
# This allows users to import pardus_gnome_greeter in their Python scripts
python = import('python')
py_installation = python.find_installation('python3', required: true)

# Get Python installation directory for dist-packages/site-packages
# Use prefix to determine correct path (/usr vs /usr/local)
prefix = get_option('prefix')
if prefix == '/usr' or prefix.startswith('/usr/')
    # System installation: use /usr/lib/python3/dist-packages
    python_site_packages = join_paths('/usr/lib', 'python3', 'dist-packages')
else
    # Local installation: use get_install_dir() which handles /usr/local correctly
    python_site_packages = py_installation.get_install_dir()
endif

# Install Python package to site-packages/dist-packages
# Exclude __main__.py as it's only for application entry point
# Exclude __pycache__ directories
install_subdir(
    'src/pardus_gnome_greeter',
    install_dir: python_site_packages,
    exclude_directories: ['__pycache__'],
    exclude_files: ['__main__.py']
)


# Executable script
configure_file(
    input: 'pardus-gnome-greeter.in',
    output: project_name,
    configuration: {
        'PYTHON': '/usr/bin/python3',
        'pkgdatadir': pkgdatadir
    },
    install: true,
    install_dir: get_option('bindir')
)

# AppData file
install_data(
    'tr.org.pardus.pardus-gnome-greeter.appdata.xml.in',
    install_dir: join_paths(datadir, 'metainfo'),
    rename: application_id + '.appdata.xml'
)

# Icon
install_data(
    'data/icons/pardus-gnome-greeter.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: application_id + '.svg'
)

# Symbolic Icons
symbolic_icons = [
  'data/icons/github-symbolic.svg',
  'data/icons/linkedin-symbolic.svg',
  'data/icons/twitter-symbolic.svg',
  'data/icons/youtube-symbolic.svg',
  'data/icons/facebook-symbolic.svg',
  'data/icons/home-symbolic.svg',
  'data/icons/document-symbolic.svg',
  'data/icons/community-symbolic.svg',
  'data/icons/forum-symbolic.svg'
]

install_data(
    symbolic_icons,
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps')
)

# Çeviri dosyalarını işle
subdir('data/po')

# GSettings Schemas
subdir('data/schemas')

install_data(
    'data/autostart/tr.org.pardus.pardus-gnome-greeter-autostart.desktop',
    install_dir: join_paths(get_option('sysconfdir'), 'xdg', 'autostart')
)

# JSON and Asset data
install_subdir('data/assets', install_dir: pkgdatadir)
install_subdir('data/css', install_dir: pkgdatadir)
install_subdir('data/json', install_dir: pkgdatadir)
install_subdir('data/ui', install_dir: pkgdatadir)

# Desktop file
i18n = import('i18n')
desktop_file = i18n.merge_file(
    input: 'tr.org.pardus.pardus-gnome-greeter.desktop.in',
    output: application_id + '.desktop',
    po_dir: join_paths(meson.current_source_dir(), 'data', 'po'),
    type: 'desktop',
    install: true,
    install_dir: join_paths(datadir, 'applications')
)

# Post-install script for manual installs (handled by dh_glib in debian)
# meson.add_install_script('meson_post_install.py')


