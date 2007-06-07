%define expat_version           2.0.1
%define glib2_version           2.6.0
%define dbus_glib_version       0.70
%define dbus_version       0.90
%define dbus_python_version 0.71

%define lib_major 1
%define lib_name %mklibname %{name} %{lib_major}

Summary: Hardware Abstraction Layer
Name: hal
Version: 0.5.9
Release: %mkrel 5
URL: http://www.freedesktop.org/Software/hal
Source0: http://freedesktop.org/~david/dist/%{name}-%{version}.tar.bz2
# (fc) 0.5.9-2mdv update to 0.5.9 branch snapshot (20070511) (GIT)
Patch0: hal-0.5.9-gitsnapshot20070511.patch
# (fc) 0.2.97-3mdk fix start order (Mdk bug #11404)
Patch3: hal-0.2.97-order.patch
# (fc) 0.4.7-9mdk fix media check on usb memory keys (Mdk bug #15070)
Patch11: hal-0.5.8.1-usbmediacheck.patch
# (couriousous) 0.5.5.1-4mdk add parallel init informations
Patch21: hal-0.5.7.1-pinit.patch
# (blino) 0.5.8.1-4mdv prefer pm-utils when available
Patch45: hal-0.5.9-prefer-pm-utils.patch
# (fc) 0.5.8.1-6mdv allow "uid" for NTFS partitions (SUSE)
Patch48: hal-allow_uid_for_ntfs.patch
# (fc) 0.5.9-2mdv fix dbus crash (Gentoo)
Patch49: hal-0.5.9-fixdbuscrash.patch

License: AFL/GPL
Group: System/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
Requires(pre): rpm-helper
Requires(preun): rpm-helper
Requires(post): rpm-helper
BuildRequires: expat-devel >= %{expat_version}
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: dbus-glib-devel >= %{dbus_glib_version}
BuildRequires: libusb-devel
BuildRequires: libcap-devel
BuildRequires: python python-devel
BuildRequires: pciutils-devel
BuildRequires: popt-devel
BuildRequires: libvolume_id-devel
BuildRequires: usbutils
#BuildRequires: policykit-devel
BuildRequires: glibc-static-devel
BuildRequires: perl-XML-Parser
BuildRequires: ImageMagick
BuildRequires: docbook-dtd412-xml
BuildRequires: intltool
BuildRequires: gtk-doc
BuildRequires: xmlto
BuildRequires: automake1.9
%if %mdkversion >= 200800
%ifarch %ix86 x86_64 ia64
BuildRequires: libsmbios-devel
%endif
%endif
Requires: dbus >= %{dbus_version}
Requires (pre): hal-info > 0.0-4.20070302.1mdv
Requires: hal-info 
#needed to get pci.ids
Requires: pciutils 
#needed to get usb.ids
Requires: usbutils
# needed for luks support
Requires: cryptsetup-luks

%description

HAL is daemon for collection and maintaining information from several
sources about the hardware on the system. It provides a live device
list through D-BUS.


%package gnome
Summary: GNOME based device manager for HAL
Group: Graphical desktop/GNOME
Requires: dbus-python >= %{dbus_python_version}
Requires: pygtk2.0-libglade >= 2.0.0
Requires: gnome-python >= 2.0.0
Requires: gnome-python-gnomevfs >= 2.0.0

%description gnome
GNOME program for displaying the devices detected by HAL

%package -n %{lib_name}
Summary: Shared library for using HAL
Group: System/Libraries
Requires: %name >= %{version}-%{release}

%description -n %{lib_name}
HAL shared library.

%package -n %{lib_name}-devel
Summary: Libraries and headers for HAL
Group: Development/C
Requires: %{name} = %{version}
Requires: %{lib_name} = %{version}
Provides: %{name}-devel = %{version}-%{release}
Provides: lib%{name}-devel = %{version}-%{release}
#gw got this from the pkgconfig file:
Requires: dbus-devel >= %{dbus_version}
Conflicts: %{_lib}hal0-devel 

%description -n %{lib_name}-devel

Headers and static libraries for HAL.


%prep
%setup -q
%patch0 -p1 -b .gitsnapshot
%patch3 -p1 -b .order
%patch11 -p1 -b .usbmediacheck
%patch21 -p1 -b .pinit
%patch45 -p1 -b .pm-utils
%patch48 -p1 -b .allow_uid_for_ntfs
%patch49 -p1 -b .fixdbuscrash

%build

%configure2_5x \
    --localstatedir=%{_var} --enable-acpi-ibm --enable-acpi-toshiba \
    --disable-selinux --disable-policy-kit --enable-umount-helper \
    --enable-docbook-docs --enable-gtk-doc --with-usb-csr \
%if %mdkversion >= 2008
%ifarch %ix86 x86_64 ia64
    --with-dell-backlight
%endif
%endif

%make

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall_std

%find_lang %{name}

cat << EOF > $RPM_BUILD_ROOT%{_datadir}/hal/fdi/policy/10osvendor/99-mandriva-storage-policy-fixed-drives.fdi
<?xml version="1.0" encoding="UTF-8"?> <!-- -*- SGML -*- --> 

<deviceinfo version="0.2">
<device>
  <match key="@block.storage_device:storage.hotpluggable" bool="false">
    <match key="@block.storage_device:storage.removable" bool="false">
      <merge key="volume.ignore" type="bool">true</merge>
    </match>
  </match>
</device>
</deviceinfo>
EOF

cat << EOF > $RPM_BUILD_ROOT%{_datadir}/hal/fdi/policy/10osvendor/90-default-policy-mount-point-names.fdi
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

install -d -m 755 $RPM_BUILD_ROOT%{_menudir}
cat >$RPM_BUILD_ROOT%{_menudir}/hal-gnome <<EOF
?package(hal-gnome): \
	command="%{_bindir}/hal-device-manager" \
	needs="X11" \
	section="Configuration/Hardware" \
	icon="hal-device-manager.png" \
	title="Device Manager" \
	longtitle="Shows information about hardware on your system" \
	startup_notify="true" \
	xdg="true"
EOF

mkdir -p %buildroot{%_liconsdir,%_miconsdir,%_iconsdir}
convert -scale 48x48 tools/device-manager/fdo-logo.png %buildroot%_liconsdir/hal-device-manager.png
convert -scale 32x32 tools/device-manager/fdo-logo.png %buildroot%_iconsdir/hal-device-manager.png
convert -scale 16x16 tools/device-manager/fdo-logo.png %buildroot%_miconsdir/hal-device-manager.png

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=Device Manager
Comment=Shows information about hardware on your system
Exec=%{_bindir}/hal-device-manager
Icon=hal-device-manager
Terminal=false
Type=Application
StartupNotify=true
Categories=GNOME;GTK;Settings;HardwareSettings;X-MandrivaLinux-System-Configuration-Hardware;
EOF

# remove unpackaged files
rm -fr $RPM_BUILD_ROOT%{_datadir}/doc/hal

%clean
rm -rf %{buildroot}

%triggerpostun -- hal < 0.2.97-3mdk
/sbin/chkconfig --del haldaemon
/sbin/chkconfig --add haldaemon


%pre
%_pre_useradd haldaemon / /sbin/nologin
%_pre_groupadd daemon haldaemon

%post -n %{lib_name} -p /sbin/ldconfig

%post
if [ "$1" = "2" -a -r %{_datadir}/hal/fdi/30osvendor/locale-policy.fdi ]; then
 mv -f %{_datadir}/hal/fdi/30osvendor/locale-policy.fdi %{_datadir}/hal/fdi/policy/10osvendor/30-locale-policy.fdi > /dev/null
fi
%_post_service haldaemon

%preun
%_preun_service haldaemon

%postun -n %{lib_name} -p /sbin/ldconfig

%post gnome
%update_menus

%postun gnome
%clean_menus

%triggerpostun -- hal < 0.5.7.1
sed -i -e "/# This file is edited by fstab-sync - see 'man fstab-sync' for details/d" -e '/.*\,managed.*/d' /etc/fstab

%files -f %{name}.lang
%defattr(-,root,root)
%doc COPYING NEWS doc/spec/docbook.css doc/spec/*.png doc/spec/*.html
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/hal.conf
%config(noreplace) %{_sysconfdir}/rc.d/init.d/*
%config(noreplace) %{_sysconfdir}/udev/rules.d/90-hal.rules
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
%{_mandir}/man1/*
%{_mandir}/man8/*

%attr(0750,haldaemon,haldaemon) %dir %{_var}/cache/hald

%{_libexecdir}/hal*

%dir %{_datadir}/hal
%{_datadir}/hal/fdi

%files -n %{lib_name}
%defattr(-,root,root)
%{_libdir}/*hal*.so.%{lib_major}*

%files -n %{lib_name}-devel
%defattr(-,root,root)
%doc doc/TODO doc/spec/*.png doc/spec/*.html
%doc %_datadir/gtk-doc/html/*
%{_libdir}/lib*.a
%{_libdir}/lib*.la
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*


%files gnome
%defattr(-,root,root)
%{_bindir}/hal-device-manager
%{_datadir}/hal/device-manager
%_menudir/hal-gnome
%_liconsdir/hal-device-manager.png
%_iconsdir/hal-device-manager.png
%_miconsdir/hal-device-manager.png
%{_datadir}/applications/*.desktop


