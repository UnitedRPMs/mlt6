%global commit0 531aa1a19df55cc378c9c79b86c7cbb187487f37
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}
# 
#%define _legacy_common_support 1

%global debug_package %{nil}

%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%bcond_with ruby
%bcond_with php

Summary:        Toolkit for broadcasters, video editors, media players, transcoders
Name:           mlt6
Version:        6.26.1
Release:        10%{?dist}

License:        GPLv3 and LGPLv2+
URL:            http://www.mltframework.org/twiki/bin/view/MLT/
Group:          System Environment/Libraries
Source0:        https://github.com/mltframework/mlt/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildRequires:  frei0r-devel
BuildRequires:  rtaudio-devel
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  opencv-devel >= 4.5.0
BuildRequires:  opencv-static >= 4.5.0
BuildRequires:  qt-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qt3d-devel
BuildRequires:  libquicktime-devel
BuildRequires:  SDL2-devel
BuildRequires:  SDL2_image-devel
BuildRequires:  SDL-devel
BuildRequires:  SDL_image-devel
BuildRequires:  gtk2-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  libogg-devel
BuildRequires:  swig >= 3.0.11
BuildRequires:	php-devel

#Deprecated dv, kino, and vorbis modules are not built.
#https://github.com/mltframework/mlt/commit/9d082192a4d79157e963fd7f491da0f8abab683f
#BuildRequires:  libdv-devel
#BuildRequires:  libvorbis-devel
BuildRequires:  libsamplerate-devel
BuildRequires:  ladspa-devel
BuildRequires:  libxml2-devel
BuildRequires:  sox-devel
BuildRequires:  swig
BuildRequires:  python3-devel
BuildRequires:	python3-setuptools
BuildRequires:  freetype-devel
BuildRequires:  libexif-devel
BuildRequires:  fftw-devel
BuildRequires:  xine-lib-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:	lua-devel
BuildRequires:	tcl-devel
BuildRequires:	ninja-build

BuildRequires:	vid.stab-devel
BuildRequires:	movit-devel
BuildRequires:	eigen3-devel
BuildRequires:	libebur128-devel
BuildRequires:	libatomic
BuildRequires:	chrpath
Provides:	mlt%{?_isa} = %{version}-%{release}

%if %{with ruby}
BuildRequires:  ruby-devel ruby
%endif

Requires:  opencv-core
Recommends:  %{name}-freeworld%{?_isa} = %{version}-%{release}


%description
MLT is an open source multimedia framework, designed and developed for 
television broadcasting.

It provides a toolkit for broadcasters, video editors,media players, 
transcoders, web streamers and many more types of applications. The 
functionality of the system is provided via an assortment of ready to use 
tools, xml authoring components, and an extendible plug-in based API.


%package devel
Summary:        Libraries, includes to develop applications with %{name}
License:        LGPLv2+
Group:          Development/Libraries
Requires:       pkgconfig
Requires:       %{name}%{?_isa} = %{version}-%{release}

%package -n python3-mlt6
Requires: python3
Requires: %{name}%{?_isa} = %{version}-%{release}
Summary: Python3 package to work with MLT

%package freeworld
BuildRequires: ffmpeg4-devel 
Requires: %{name}%{?_isa} = %{version}-%{release}
Summary: Freeworld support part of MLT.


%description devel
The %{name}-devel package contains the header files and static libraries for
building applications which use %{name}.

%description -n python3-mlt6
This module allows to work with MLT using python. 


%description freeworld
This package give us the freeworld (ffmpeg support) part of MLT.


%prep
%autosetup -n mlt-%{commit0} -p1
chmod 644 src/modules/qt/kdenlivetitle_wrapper.cpp
chmod 644 src/modules/kdenlive/filter_freeze.c
chmod -x demo/demo

# Don't overoptimize (breaks debugging)
sed -i -e '/fomit-frame-pointer/d' configure
sed -i -e '/ffast-math/d' configure

# respect CFLAGS LDFLAGS when building shared libraries. Bug #308873
	for x in python lua; do
		sed -i "/mlt.so/s: -lmlt++ :& ${CFLAGS} ${LDFLAGS} :" src/swig/$x/build || die
	done

# swig fix
sed -i "/^LDFLAGS/s: += :& ${LDFLAGS} :" src/swig/ruby/build

%if 0%{?fedora} >= 26
# xlocale.h is gone in F26/RAWHIDE
sed -r -i 's/#include <xlocale.h>/#include <locale.h>/' src/framework/mlt_property.h
%endif

# Change shebang in all relevant files in this directory and all subdirectories
# See `man find` for how the `-exec command {} +` syntax works
find src/swig/python -name '*.py' | xargs sed -i '1s|^#!/usr/bin/env python|#!%{__python3}|'


%build

#export STRIP=/bin/true
./configure --prefix=%{_prefix} 		\
	--libdir=%{_libdir} 			\
	--avformat-swscale 			\
        --enable-gpl                            \
        --enable-gpl3                           \
        --enable-motion-est                     \
%ifarch ppc ppc64
        --disable-mmx                           \
        --disable-sse                           \
        --disable-xine                          \
%endif
        --rename-melt=mlt-melt              	\
        --swig-languages="python"

make %{?_smp_mflags}


%install

# https://fedoraproject.org/wiki/Changes/Avoid_usr_bin_python_in_RPM_Build#Quick_Opt-Out
export PYTHON_DISALLOW_AMBIGUOUS_VERSION=0

make DESTDIR=%{buildroot} install

# manually do what 'make install' skips
install -D -pm 0644 src/swig/python/mlt.py %{buildroot}%{python3_sitelib}/mlt.py
install -D -pm 0755 src/swig/python/_mlt.so %{buildroot}%{python3_sitearch}/_mlt.so

mv src/modules/motion_est/README README.motion_est


%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc AUTHORS NEWS README*
%license COPYING GPL
%{_bindir}/mlt-melt
%{_libdir}/mlt/
%{_libdir}/libmlt++.so.*
%{_libdir}/libmlt.so.*
%{_datadir}/mlt/

%files -n python3-mlt6
%{python3_sitelib}/mlt.py*
%{python3_sitearch}/_mlt.so
%{python3_sitelib}/__pycache__/mlt.*


%files devel
%doc docs/* demo/
%{_libdir}/pkgconfig/mlt-framework.pc
%{_libdir}/pkgconfig/mlt++.pc
%{_libdir}/libmlt.so
%{_libdir}/libmlt++.so
%{_includedir}/mlt/
%{_includedir}/mlt++/


%files freeworld 
%{_libdir}/mlt/libmltavformat.so



%changelog

* Sun May 22 2022 Unitedrpms Project <unitedrpms AT protonmail DOT com> 6.26.1-4
- Initial build
