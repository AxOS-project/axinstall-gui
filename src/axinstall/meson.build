pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'axinstall')
gnome = import('gnome')

gnome.compile_resources('axinstall',
  'axinstall.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'axinstall.in',
  output: 'axinstall',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

subdir('widgets')
subdir('functions')
subdir('classes')
subdir('locales')
subdir('utils')
subdir('scripts')

axinstall_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'keymaps.py',
  'desktops.py',
  'manualpartitioning.py'
]

install_data(axinstall_sources, install_dir: moduledir)
