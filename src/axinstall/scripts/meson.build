pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
scriptsdir = join_paths(pkgdatadir, 'axinstall/scripts')

axinstall_sources = [
    'getDisks.sh',
    'getDiskSize.sh',
    'checkEFI.sh',
    'install.sh',
    'savePrefs.sh',
    'getDiskType.sh',
    'getDiskName.sh',
    'getPartitions.sh',
    'reboot.sh',
    'openBash.sh',
    'openGparted.sh',
]
install_data(axinstall_sources, install_dir: scriptsdir)