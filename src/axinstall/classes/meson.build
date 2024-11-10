pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
classesdir = join_paths(pkgdatadir, 'axinstall/classes')

axinstall_sources = [
    '__init__.py',
    'locale.py',
    'keymap.py',
    'install_prefs.py',
    'partition.py',
    'axinstall_screen.py'
]
install_data(axinstall_sources, install_dir: classesdir)
