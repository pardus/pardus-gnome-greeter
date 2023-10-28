project('pardus-gnome-greeter',  version: '0.0.9')

# Configuration
gnome = import('gnome')

prefix = get_option('prefix')
sysconfdir = get_option('sysconfdir')

data_dir = join_paths(prefix,get_option('datadir'))
schema_dir = join_paths(prefix, 'share', 'glib-2.0','schemas')
icon_dir = join_paths(prefix,'share','icons','hicolor','scalable','apps')
auto_start_dir = join_paths(sysconfdir,'skel','.config','autostart')
desktop_file = 'tr.org.pardus.pardus-gnome-greeter.desktop'

desktop_file_dir = join_paths(prefix,'share','applications')

#Source files
source_dir = join_paths(prefix , 'share' , 'pardus' , 'pardus-gnome-greeter')
install_data([desktop_file],install_dir : desktop_file_dir)
install_data(['pardus-gnome-greeter.svg'],install_dir:icon_dir)
install_data(['pardus-gnome-greeter','pardus-gnome-greeter.svg'], install_dir : source_dir)
install_data([desktop_file],install_dir : auto_start_dir)

install_subdir('data',install_dir : source_dir)
install_subdir('src',install_dir : source_dir)



install_data(['pardus-gnome-greeter'], install_dir : prefix / 'bin')
subdir('data/schema')


# locale settings
subdir('data/po')


