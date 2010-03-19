%define name    ike
%define version 2.1.6
%define release %mkrel 0.beta4.5
%define major		2
%define libname		%mklibname %{name} %{major}

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Ipsec client with GUI
License:	Sleepycat
Group:		Networking/Remote access
URL:		http://www.shrew.net/
Source0:	http://www.shrew.net/download/ike/%{name}-%{version}-beta-4.tbz2
Source1:	iked.conf
Source2:	iked.init
Source3:	README.urpmi
BuildRequires:  openssl-devel
BuildRequires:  libldap-devel
BuildRequires:	flex
BuildRequires:  bison
BuildRequires:	cmake
BuildRequires:	qt3-devel
BuildRequires:	imagemagick
Requires:	logrotate
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
The Shrew Soft VPN Client for Unix is a free IPsec Client for FreeBSD, NetBSD and 
Linux based operating systems. This version is distributed under an OSI approved 
open source license and is hosted in a public subversion repository. It supports 
most of the features availalble in the Windows VPN Client version with the exception 
of those which are not cross platform compatible. 

%package -n	qt-%{name}
Summary:	Qt GUI for ike vpn
Group:		Networking/Remote access
Requires:	%{name} = %{version}-%{release}

%description -n	qt-%{name}
A Qt gui for the ike VPN client

%package -n	%{libname}
Summary:	Main library for ike
Group:		System/Libraries
Provides:	lib%{name} = %{version}-%{release}

%description -n	%{libname}
This package contains the library needed to run programs dynamically
linked with ike

%prep

%setup -q -n %{name}

#put iked log in its own dir
sed -i 's:/var/log/:/var/log/iked/:' source/iked/iked.conf.sample

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
# using cmake macro breaks build
cmake .	-DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
	-DETCDIR=%{_sysconfdir} \
	-DQTGUI=YES \
	-DNATT=yes \
	-DLDAP=yes \
	-DTESTS=yes

%make

%install
rm -rf %{buildroot}

#fix lib path on 64 bit arches
%ifarch x86_64 ppc64 sparc64 s390x
sed -i 's:{CMAKE_INSTALL_PREFIX}/lib:{CMAKE_INSTALL_PREFIX}/lib64:' source/libike/cmake_install.cmake
sed -i 's:{CMAKE_INSTALL_PREFIX}/lib:{CMAKE_INSTALL_PREFIX}/lib64:' source/libpfk/cmake_install.cmake
%endif

%makeinstall_std

%{__install} -m644 %{SOURCE1} -D %{buildroot}%{_sysconfdir}/iked.conf
%{__install} -m755 %{SOURCE2} -D %{buildroot}%{_initrddir}/iked
mkdir -p %{buildroot}%{_docdir}/%{name}
%{__install} -m750 *.TXT -D %{buildroot}%{_docdir}/%{name}
%{__install} -m750 %{SOURCE3} -D %{buildroot}%{_docdir}/%{name}
%{__install} -d -p %{buildroot}%{_localstatedir}/run/%{name}d
%{__install} -d -p %{buildroot}%{_localstatedir}/log/%{name}d

mkdir -p %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48,64x64}/apps
install -m0644 source/ikea/png/ikea.png %{buildroot}%{_iconsdir}/hicolor/64x64/apps/%{name}.png
convert -scale 48x48 source/ikea/png/ikea.png %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{name}.png
convert -scale 32x32 source/ikea/png/ikea.png %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
convert -scale 16x16 source/ikea/png/ikea.png %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png

# Create /etc/logrotate.d/ike
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} << EOF
/var/log/%{name}/*.log {
       weekly
       rotate 10
       copytruncate
       delaycompress
       compress
       notifempty
       missingok
}
EOF

#menu entry
%{__mkdir_p} %{buildroot}%{_datadir}/applications
%{__cat} > %{buildroot}%{_datadir}/applications/mandriva-qt-%{name}.desktop << EOF
[Desktop Entry]
Name=Qt Ike VPN
Comment=Qt GUI for ike vpn
Exec=%{_bindir}/ikea
Icon=%{name}
Terminal=false
Type=Application
Categories=Qt;Network;
EOF

%clean
%{__rm} -rf %{buildroot}

%if %mdkversion < 200900
%post
%_post_service iked
%endif

%if %mdkversion < 200900
%preun
%_preun_service iked
%endif


%files
%defattr(-,root,root,-)
%doc %{_docdir}/%{name}/*.TXT 
%doc %{_docdir}/%{name}/README.urpmi
%config(noreplace) %{_sysconfdir}/iked.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/ike
%{_sysconfdir}/iked.conf.sample
%{_initrddir}/iked
%{_sbindir}/iked
%{_mandir}/man5/*.5*
%{_mandir}/man8/*.8*
%dir %{_localstatedir}/run/%{name}d
%dir %{_localstatedir}/log/%{name}d

%files -n qt-ike
%defattr(0755,root,root)
%{_bindir}/ike*
%{_datadir}/applications/mandriva-qt-ike.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.png
%{_mandir}/man1/*.1*

%files -n %{libname}
%defattr(-, root, root)
%{_libdir}/*.so.%{major}*
%exclude %{_libdir}/*.so

