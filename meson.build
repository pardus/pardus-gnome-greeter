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

# Python sources
install_subdir(
    'src/pardus_gnome_greeter',
    install_dir: pkgdatadir
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

# Symbolic Icons for social media
install_data(
    'data/icons/github.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'github-symbolic.svg'
)

install_data(
    'data/icons/linkedin.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'linkedin-symbolic.svg'
)

install_data(
    'data/icons/twitter.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'twitter-symbolic.svg'
)

install_data(
    'data/icons/youtube.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'youtube-symbolic.svg'
)

install_data(
    'data/icons/facebook.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'facebook-symbolic.svg'
)

# Symbolic Icons for useful links
install_data(
    'data/icons/home.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'home-symbolic.svg'
)

install_data(
    'data/icons/document.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'document-symbolic.svg'
)

install_data(
    'data/icons/community.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'community-symbolic.svg'
)

install_data(
    'data/icons/forum.svg',
    install_dir: join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps'),
    rename: 'forum-symbolic.svg'
)

# Çeviri dosyalarını işle
subdir('data/po')

# GSettings Schemas
subdir('data/schemas')

# JSON and Asset data
install_subdir('data/assets', install_dir: pkgdatadir)
install_subdir('data/css', install_dir: pkgdatadir)
install_subdir('data/json', install_dir: pkgdatadir)
install_subdir('data/ui', install_dir: pkgdatadir)

# Post-install script for manual installs (handled by dh_glib in debian)
# meson.add_install_script('meson_post_install.py')


