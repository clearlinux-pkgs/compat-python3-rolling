Name:           compat-python3-rolling
Version:        3.12.7
Release:        1
License:        Python-2.0
Summary:        The Python Programming Language
Url:            https://www.python.org
Group:          devel/python
Source0:        https://www.python.org/ftp/python/3.12.7/Python-3.12.7.tar.xz
Source1:        usrlocal.pth
Patch1:         0001-Fix-python-path-for-linux.patch
Patch2:         0002-test_socket.py-remove-testPeek-test.test_socket.RDST.patch

# Suppress stripping binaries
%define __strip /bin/true
%define debug_package %{nil}



BuildRequires:  bzip2
BuildRequires:  db
BuildRequires:  grep
BuildRequires:  bzip2-dev
BuildRequires:  xz-dev
BuildRequires:  gdbm-dev
BuildRequires:  readline-dev
BuildRequires:  openssl
BuildRequires:  openssl-dev
BuildRequires:  sqlite-autoconf
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  ncurses-dev
BuildRequires:  expat-dev
BuildRequires:  libffi-dev
BuildRequires:  procps-ng-bin
BuildRequires:  netbase
BuildRequires:  tk-dev
BuildRequires:  tk-extras
BuildRequires:  tk-staticdev
BuildRequires:  tcl-dev
BuildRequires:  tcl-staticdev
BuildRequires:  libX11-dev
BuildRequires:  pypi-pip
BuildRequires:  util-linux-dev
Requires: compat-python3-rolling-core
Requires: compat-python3-rolling-lib
Requires: pypi-pip

%define keepstatic 1
%global __arch_install_post %{nil}

%description
The Python Programming Language.

%package lib
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel/python

%description lib
The Python Programming Language.
%package staticdev
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel/python

%description staticdev
The Python Programming Language.

%package core
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel/python

%description core
The Python Programming Language.

%package dev
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel
Requires:       compat-python3-rolling-lib
Requires:       compat-python3-rolling-core

%package tcl
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel
Requires:       compat-python3-rolling-lib
Requires:       compat-python3-rolling-core

%package xz-lzma
License:        Python-2.0
Summary:        The Python Programming Language
Group:          devel
Requires:       compat-python3-rolling-lib
Requires:       compat-python3-rolling-core

%define python_configure_flags --with-threads --with-pymalloc  --without-cxx-main --with-signal-module --enable-ipv6=yes  --libdir=/usr/lib  ac_cv_header_bluetooth_bluetooth_h=no  ac_cv_header_bluetooth_h=no  --with-system-ffi --with-system-expat --with-lto --with-computed-gotos --without-ensurepip --enable-optimizations


%description dev
The Python Programming Language.

%description tcl
The Python Programming Language.

%description xz-lzma
Support for XZ/LZMA compression in Python.

%prep
%setup -q -n Python-%{version}
%patch -P 1 -p1
%patch -P 2 -p1

pushd ..
cp -a Python-%{version} Python-shared
popd

%build
export INTERMEDIATE_CFLAGS="$CFLAGS -O3 -fno-semantic-interposition -g1 -gno-column-info -gno-variable-location-views -gz  "
export INTERMEDIATE_CXXFLAGS="$CXXFLAGS -O3 -fno-semantic-interposition -g1 -gno-column-info -gno-variable-location-views -gz "
export AR=gcc-ar
export RANLIB=gcc-ranlib
export NM=gcc-nm
export LANG=C

export CC=/usr/bin/gcc
unset HOSTCC
unset HOSTCFLAGS
unset HOSTRUNNER
export CFLAGS="$INTERMEDIATE_CFLAGS -Wl,-z,x86-64-v2 "
export CXXFLAGS="$INTERMEDIATE_CXXFLAGS "
%configure %python_configure_flags
PROFILE_TASK="-m test --pgo-extended" make profile-opt %{?_smp_mflags}

pushd ../Python-shared
%configure %python_configure_flags --enable-shared
PROFILE_TASK="-m test --pgo-extended" make profile-opt %{?_smp_mflags}
popd

%install
export AR=gcc-ar
export RANLIB=gcc-ranlib
export NM=gcc-nm
export CFLAGS="$CFLAGS -O3 -fno-semantic-interposition -g1 -gno-column-info -gno-variable-location-views -gz "
export CXXFLAGS="$CXXFLAGS -O3 -fno-semantic-interposition -g1 -gno-column-info -gno-variable-location-views -gz "
export LDFLAGS="$LDFLAGS -g1 -gz"

%make_install
mkdir -p %{buildroot}/usr/lib64/
mv %{buildroot}/usr/lib/libpython*.a %{buildroot}/usr/lib64/

# Toss in the one off built dynamic libpython
# This is only built once as things that link against it are picky
# if the same python that it links against at build time is different
# than at runtime, so we can't use an alternate optimized version.
mv ../Python-shared/libpython3.12.so.1.0 %{buildroot}/usr/lib64/
mv ../Python-shared/libpython3.so %{buildroot}/usr/lib64/

# Configure Python to return the dynamic libpython instead of the static lib for certain config variables
sed -i "s|\('BLDLIBRARY':\s*\)'libpython\([0-9\.]*\).a'|\1'-L. -lpython\2'|" %{buildroot}/usr/lib/python3.12/_sysconfigdata__linux_x86_64-linux-gnu.py
sed -i "s|\('INSTSONAME':\s*'libpython[0-9\.]*\).a\('\)|\1.so\2|" %{buildroot}/usr/lib/python3.12/_sysconfigdata__linux_x86_64-linux-gnu.py
sed -i "s|\('LDLIBRARY':\s*'libpython[0-9\.]*\).a\('\)|\1.so\2|" %{buildroot}/usr/lib/python3.12/_sysconfigdata__linux_x86_64-linux-gnu.py

# Add /usr/local/lib/python*/site-packages to the python path
install -m 0644 %{SOURCE1} %{buildroot}/usr/lib/python3.12/site-packages/usrlocal.pth

ln -s libpython3.12.so.1.0 %{buildroot}/usr/lib64/libpython3.12.so

# Post fixup for libdir in the .pc file
sed -i'' -e 's|libdir=${exec_prefix}/lib|libdir=${exec_prefix}/lib64|' %{buildroot}/usr/lib64/pkgconfig/python-3.12-embed.pc
sed -i'' -e 's|libdir=${exec_prefix}/lib|libdir=${exec_prefix}/lib64|' %{buildroot}/usr/lib64/pkgconfig/python-3.12.pc

# remove non minor version files
rm -f %{buildroot}/usr/bin/2to3
rm -f %{buildroot}/usr/bin/idle3
rm -f %{buildroot}/usr/bin/pydoc3
rm -f %{buildroot}/usr/bin/python3
rm -f %{buildroot}/usr/bin/python3-config
rm -f %{buildroot}/usr/lib64/libpython3.so
rm -f %{buildroot}/usr/lib64/pkgconfig/python3.pc
rm -f %{buildroot}/usr/lib64/pkgconfig/python3-embed.pc
rm -f %{buildroot}/usr/share/man/man1/python3.1


%files

%files lib
/usr/lib64/libpython3.12.so.1.0

%files staticdev
/usr/lib/python3.12/config-3.12-x86_64-linux-gnu/libpython3.12.a
/usr/lib64//libpython3.12.a

%files core
/usr/bin/2to3-3.12
/usr/bin/pydoc3.12
/usr/bin/python3.12
/usr/bin/python3.12-config
/usr/lib/python3.12
/usr/share/man/man1/python3.12.1

%exclude /usr/lib/python3.12/lib-dynload/_tkinter.cpython-312-x86_64-linux-gnu.so
%exclude /usr/lib/python3.12/tkinter
%exclude /usr/lib/python3.12/config-3.12-x86_64-linux-gnu/libpython3.12.a
%exclude /usr/lib/python3.12/lib-dynload/_lzma.cpython-312-x86_64-linux-gnu.so

%files dev
/usr/include/python3.12/*.h
/usr/include/python3.12/cpython/*.h
/usr/include/python3.12/internal/*.h
/usr/lib64/libpython3.12.so
/usr/lib64/pkgconfig/python-3.12.pc
/usr/lib64/pkgconfig/python-3.12-embed.pc


%files tcl
/usr/bin/idle3.12
/usr/lib/python3.12/tkinter
/usr/lib/python3.12/lib-dynload/_tkinter.cpython-312-x86_64-linux-gnu.*

%files xz-lzma
/usr/lib/python3.12/lib-dynload/_lzma.cpython-312-x86_64-linux-gnu.so
