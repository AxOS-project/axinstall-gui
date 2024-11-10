pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
utilsdir = join_paths(pkgdatadir, 'axinstall/utils')

axinstall_sources = [
    '__init__.py',
    'disks.py',
    'threading.py',
    'command.py',
    'gtk_helpers.py'
]
install_data(axinstall_sources, install_dir: utilsdir)
