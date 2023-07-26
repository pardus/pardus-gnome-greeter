project('pardus-gnome-greeter',  version: '0.0.1')

# Configuration
gnome = import('gnome')

prefix = get_option('prefix')
data_dir = join_paths(prefix,get_option('datadir'))
schema_dir = join_paths(prefix, 'share', 'pardus', 'pardus-gnome-greeter')

#Source files
source_dir = join_paths(prefix , 'share' , 'pardus' , 'pardus-gnome-greeter')
install_data(['pardus-gnome-greeter','pardus-gnome-greeter.svg'], install_dir : source_dir)
install_subdir('data',install_dir : source_dir)
install_subdir('src',install_dir : source_dir)

install_data(['pardus-gnome-greeter'], install_dir : prefix / 'bin')
