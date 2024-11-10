pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
localesdir = join_paths(pkgdatadir, 'axinstall/locales')

axinstall_sources = [
    '__init__.py',
    'africa.py',
    'america.py',
    'antarctica.py',
    'arctic.py',
    'asia.py',
    'atlantic.py',
    'australia.py',
    'brazil.py',
    'canada.py',
    'chile.py',
    'europe.py',
    'indian.py',
    'mexico.py',
    'pacific.py',
    'locales_list.py',
]
install_data(axinstall_sources, install_dir: localesdir)