%define expat_version           1.95.5
%define glib2_version           2.14.0
%define dbus_glib_version       0.70
%define dbus_version       0.90
%define dbus_python_version 0.71

%define lib_major 1
%define lib_name %mklibname %{name} %{lib_major}

%define develname %mklibname %{name} -d
%if %mdkversion < 200800
%define develname %mklibname %{name} %{lib_major} -d
%endif

%define prerel rc1.20090403
%define snapshot ~rc1+git20090403

%define git_url git://git.freedesktop.org/git/hal

Summary: Hardware Abstraction Layer
Name: hal
Version: 0.5.14
Release: %mkrel 6
URL: http://www.freedesktop.org/Software/hal
Source0: http://hal.freedesktop.org/releases/%{name}-%{version}.tar.bz2
Source1: 10-elantech-touchpad.fdi
# (fc) 0.2.97-3mdk fix start order (Mdk bug #11404)
# (aw) updated 0.5.11-8, messagebus has moved later
Patch3: hal-0.5.11-order.patch
# (couriousous) 0.5.5.1-4mdk add parallel init informations
Patch21: hal-0.5.11-pinit.patch
# (fc) 0.5.14-1mdv fix umount helper crash (GIT) (Mdv bug #57138)
Patch22: hal-0.5.14-fix-umount-crash.patch
# (fc) 0.5.14-3mdv fix input helper crash (GIT)
Patch23: hal-0.5.14-fix-input-crash.patch
# (bor) fix crash on unhandled rule (GIT) (mdv #60790)
Patch24: hal-0.5.14-do-not-crash-on-unhandled-rule.patch
Patch25: hal-0.5.14-libv4l_header_fix.diff
Patch26: hal-0.5.14-fix-build-with-current-glib.patch

License: GPLv2 or AFL
Group: System/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
Requires(pre): rpm-helper
Requires(preun): rpm-helper
Requires(post): rpm-helper
Requires(post): chkconfig >= 1.3.37-3mdv
BuildRequires: expat-devel >= %{expat_version}
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: dbus-glib-devel >= %{dbus_glib_version}
BuildRequires: libusb-devel
BuildRequires: libcap-devel
BuildRequires: python python-devel
BuildRequires: pciutils-devel
BuildRequires: zlib-devel
BuildRequires: popt-devel
BuildRequires: usbutils
BuildRequires: glibc-static-devel
BuildRequires: perl(XML::Parser)
BuildRequires: docbook-dtd412-xml
BuildRequires: intltool
BuildRequires: gtk-doc
BuildRequires: xmlto
BuildRequires: gperf
%if %mdkversion >= 200800
%if %mdkversion >= 200900
BuildRequires: consolekit-devel >= 0.3.0
%else
BuildRequires: consolekit-devel
%endif
%if %mdkversion < 200910
%ifarch %ix86 x86_64 ia64
BuildRequires: libsmbios-devel
%endif
%endif
%endif
%if %mdkversion >= 200810
BuildRequires: pkgconfig(polkit)
%endif
BuildRequires: libblkid-devel
BuildRequires: libv4l-devel
Requires: dbus >= %{dbus_version}
Requires(pre): hal-info > 0.0-4.20070302.1mdv
Requires(post): %{lib_name} >= %{version}-%{release}
Requires: hal-info 
#needed to get pci.ids
Requires: pciutils 
#needed to get usb.ids
Requires: usbutils
# needed for luks support
Requires: cryptsetup-luks
%if %mdkversion >= 200810
Requires: policykit
Requires: acl
Requires(pre): policykit >= 0.7
%endif
Requires: %mklibname blkid 1

%description
HAL is daemon for collection and maintaining information from several
sources about the hardware on the system. It provides a live device
list through D-BUS.

%package -n %{lib_name}
Summary: Shared library for using HAL
Group: System/Libraries
Requires: %name >= %{version}-%{release}

%description -n %{lib_name}
HAL shared library.

%package -n %{develname}
Summary: Libraries and headers for HAL
Group: Development/C
Requires: %{name} = %{version}
Requires: %{lib_name} = %{version}
Provides: %{name}-devel = %{version}-%{release}
Provides: lib%{name}-devel = %{version}-%{release}
#gw got this from the pkgconfig file:
Requires: dbus-devel >= %{dbus_version}
Conflicts: hal < 0.5.10-0.rc2.3mdv2008.0
Conflicts: %{_lib}hal0-devel
%if %mdkversion >= 200800
Obsoletes: %{lib_name}-devel
%endif

%description -n %{develname}
Headers and static libraries for HAL.

%prep
%setup -q 
%patch3 -p1 -b .order
%patch21 -p1 -b .pinit
%patch22 -p1 -b .fix-umount-crash
%patch23 -p1 -b .fix-input-crash
%patch24 -p1 -b .fix-unhandled-rule-crash
%patch25 -p0 -b .libv4l_header_fix
%patch26 -p1 -b .cur_glib~

%build

%define _libexecdir %{_libdir}/hal

%configure2_5x \
    --localstatedir=%{_var} --enable-acpi-ibm --enable-acpi-toshiba \
    --enable-umount-helper \
    --enable-docbook-docs --enable-gtk-doc --with-usb-csr \
    --with-udev-prefix=/lib \
%if %mdkversion < 200810
    --disable-policy-kit \
%else
    --enable-policy-kit \
%if %mdkversion < 201000
    --enable-acl-management \
%endif
%endif
%if %mdkversion >= 200800
%ifarch %ix86 x86_64 ia64
%if %mdkversion >= 200910
    --disable-smbios \
    --without-dell-backlight \
%else
    --with-dell-backlight \
%endif
%endif
    --enable-console-kit \
%else
    --disable-console-kit \
%endif


make

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/%{_var}/run/hald

%makeinstall_std

cat << EOF > %{buildroot}%{_datadir}/hal/fdi/policy/10osvendor/90-default-policy-mount-point-names.fdi
<?xml version="1.0" encoding="ISO-8859-1"?> <!-- -*- SGML -*- --> 

<deviceinfo version="0.2">
  <device>
    <match key="info.category" string="volume">
	<match key="@block.storage_device:portable_audio_player.type" string="ipod">
      		<append key="volume.policy.desired_mount_point" type="string">ipod</append>
    	</match>
    	<match key="@block.storage_device:storage.drive_type" string="floppy">
		<append key="volume.policy.desired_mount_point" type="string">floppy</append>
	</match>
    </match>
  </device>
</deviceinfo>
EOF

# fix Mdv bug #41204
install -m644 %{SOURCE1} %{buildroot}%{_datadir}/hal/fdi/policy/10osvendor

%clean
rm -rf %{buildroot}

%triggerpostun -- hal < 0.5.11-8
/sbin/chkconfig --del haldaemon
/sbin/chkconfig --add haldaemon

%pre
%_pre_useradd haldaemon / /sbin/nologin
%_pre_groupadd daemon haldaemon
# User haldaemon needs to be able to read authorizations
%{_bindir}/polkit-auth --user haldaemon --grant org.freedesktop.policykit.read >& /dev/null || :

%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif

%post
if [ "$1" = "2" -a -r %{_datadir}/hal/fdi/30osvendor/locale-policy.fdi ]; then
 mv -f %{_datadir}/hal/fdi/30osvendor/locale-policy.fdi %{_datadir}/hal/fdi/policy/10osvendor/30-locale-policy.fdi > /dev/null
fi
%_post_service haldaemon

%preun
%_preun_service haldaemon

%triggerpostun -- hal < 0.5.12-0.rc1.2mdv
/sbin/chkconfig --level 7 haldaemon reset

%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%triggerpostun -- hal < 0.5.7.1
sed -i -e "/# This file is edited by fstab-sync - see 'man fstab-sync' for details/d" -e '/.*\,managed.*/d' /etc/fstab

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/hal.conf
%config(noreplace) %{_sysconfdir}/rc.d/init.d/*
/lib/udev/rules.d/90-hal.rules
%dir %{_sysconfdir}/hal/
%{_sysconfdir}/hal/fdi
/sbin/umount.hal
%{_sbindir}/*
%{_bindir}/lshal
%{_bindir}/hal-device
%{_bindir}/hal-get-property
%{_bindir}/hal-set-property
%{_bindir}/hal-find-by-capability
%{_bindir}/hal-find-by-property
%{_bindir}/hal-is-caller-locked-out
%{_bindir}/hal-disable-polling
%{_bindir}/hal-lock
%{_bindir}/hal-setup-keymap
%if %mdkversion >= 200810
%{_bindir}/hal-is-caller-privileged
%{_datadir}/PolicyKit/policy/*
%attr(0750,haldaemon,haldaemon) %dir %{_var}/run/hald
%endif
%{_mandir}/man1/*
%{_mandir}/man8/*

%attr(0750,haldaemon,haldaemon) %dir %{_var}/cache/hald

%{_libexecdir}/*

%dir %{_datadir}/hal
%{_datadir}/hal/fdi

%files -n %{lib_name}
%defattr(-,root,root)
%{_libdir}/*hal*.so.%{lib_major}*

%files -n %{develname}
%defattr(-,root,root)
%doc %{_docdir}/hal/spec
%doc %_datadir/gtk-doc/html/*
%{_libdir}/lib*.a
%{_libdir}/lib*.la
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
