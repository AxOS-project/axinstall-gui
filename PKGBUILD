pkgname=axinstall
pkgver=1.11
pkgrel=2
pkgdesc="AxOS installer"
arch=('x86_64')
license=('GPL')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'python-cairo' 'openssl' 'python-pytz' 'gnome-disk-utility' 'vte4' 'meson' 'ninja' 'libadwaita' 'desktop-file-utils' 'appstream-glib' 'python-urllib3' 'python-tzlocal' 'python-requests' 'gtksourceview5' 'python-regex' 'python-psutil' 'axinstall-cli')
# sha256sums=('SKIP') 

build() {
  cd "${srcdir}"
  meson --prefix=/usr _build --reconfigure
  ninja -C _build
}

package() {
  cd "${srcdir}/_build"
  DESTDIR="${pkgdir}" ninja install
}
