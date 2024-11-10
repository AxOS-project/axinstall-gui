pkgname=axinstall
pkgver=0.2.3
pkgrel=1
pkgdesc="AxOS installer"
arch=('x86_64')
license=('GPL')
depends=('python' 'python-gobject' 'gtk4' 'libadwaita' 'python-cairo' 'openssl' 'python-pytz' 'gparted' 'vte4' 'meson' 'ninja' 'libadwaita' 'desktop-file-utils' 'appstream-glib' 'python-urllib3' 'python-tzlocal' 'python-requests' 'gtksourceview5' 'python-regex')
# sha256sums=('SKIP') 

build() {
  cd "${srcdir}"
  meson --prefix=/usr _build
  ninja -C _build
}

package() {
  cd "${srcdir}/_build"
  DESTDIR="${pkgdir}" ninja install
}
