project('pardus-gnome-greeter', 'python', version: '0.0.1')

# Configuration
gnome = import('gnome')
pkg = import('python')

# Source files
src = subdir('src')

# Data files
data = subdir('data')


# Target: The main executable
greeter_exe = executable('pardus-gnome-greeter', 
                         src.join('Main.py'),
                         dependencies : [gnome, pkg],
)

# Target: Install data files
install_data(data,
             install_dir : get_option('prefix') / 'share' / 'pardus' / 'pardus-gnome-greeter',
)


# Dependencies
pygobject_dep = dependency('pygobject-3.0', version: '>=3.0')
py_dep = dependency('python3')

# Targets: Adding dependencies
greeter_exe.add_depencency(pygobject_dep)
greeter_exe.add_depencency(py_dep)
