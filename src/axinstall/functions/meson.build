pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
functionsdir = join_paths(pkgdatadir, 'axinstall/functions')

axinstall_sources = [
    '__init__.py',
    'keyboard_screen.py',
    'timezone_screen.py',
    'locale_screen.py',
    'user_screen.py',
    'desktop_screen.py',
    'misc_screen.py',
    'partition_screen.py',
    'summary_screen.py',
    'install_screen.py',
    'finished_screen.py',
    'welcome_screen.py',
    'kernel_screen.py',
]
install_data(axinstall_sources, install_dir: functionsdir)
