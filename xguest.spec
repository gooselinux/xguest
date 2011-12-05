Summary: Creates xguest user as a locked down user 
Name: xguest
Version: 1.0.8
Release: 6%{?dist}
License: GPLv2+
Group: System Environment/Base
BuildArch: noarch
Source: http://people.fedoraproject.org/~dwalsh/xguest/%{name}-%{version}.tar.bz2
patch: xguest-namespace.patch
URL: http://people.fedoraproject.org/~dwalsh/xguest/

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires(post): pam >= 0.99.8.1-17 selinux-policy > 3.6.3-12 selinux-policy-base
Requires(post): policycoreutils-sandbox
Requires(post): sabayon-apply
Requires: gdm >= 1:2.20.0-15.fc8

%description
Installing this package sets up the xguest user to be used as a temporary
account to switch to or as a kiosk user account. The account is disabled unless
SELinux is in enforcing mode. The user is only allowed to log in via gdm.
The home and temporary directories of the user will be polyinstantiated and
mounted on tmpfs.

%prep
%setup -q
%patch -p1 -b .namespace

%build

%clean
%{__rm} -fR %{buildroot}

%install
%{__rm} -fR %{buildroot}
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/sabayon
%{__mkdir} -p %{buildroot}/%{_sysconfdir}/security/namespace.d/ls
install -m0644 xguest.zip %{buildroot}/%{_sysconfdir}/sabayon/
install -m0644 xguest.conf %{buildroot}/%{_sysconfdir}/security/namespace.d/

%post
if [ $1 -eq 1 ]; then
useradd -c "kiosk" xguest 2> /dev/null | :
echo "xguest:exclusive" >> /etc/security/sepermit.conf

semanage -S targeted -i - << _EOF
login -a -s xguest_u xguest 
boolean -m --on allow_polyinstantiation
boolean -m --on xguest_connect_network
boolean -m --on xguest_mount_media
boolean -m --on xguest_use_bluetooth
_EOF

# Add two directories to /etc/skell so pam_namespace will label properly
mkdir /etc/skel/.mozilla 2> /dev/null
mkdir /etc/skel/.gnome2 2> /dev/null

/usr/bin/python << __eof
from sabayon import systemdb
db = systemdb.get_user_database()
db.set_profile("xguest", "xguest.zip")
__eof

fi

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/sabayon/xguest.zip
%{_sysconfdir}/security/namespace.d/
%doc README LICENSE

%preun
if [ $1 -eq 0 ]; then
sed -i '/^xguest/d' /etc/security/sepermit.conf

/usr/bin/python << __eof
from sabayon import systemdb
db = systemdb.get_user_database()
db.set_profile("xguest", "")
__eof

fi

%changelog
* Wed Apr 28 2010 Dan Walsh <dwalsh@redhat.com> - 1.0.8-6
- Fix build to work on disabled machine
Resolves: #507609

* Wed Mar 10 2010 Dan Walsh <dwalsh@redhat.com> - 1.0.8-5
- Use /proc/self/fd/0 instead of /dev/stdin

* Tue Mar 2 2010 Dan Walsh <dwalsh@redhat.com> - 1.0.8-4
- Use /proc/self/0 instead of /dev/stdin

* Tue Feb 9 2010 Dan Walsh <dwalsh@redhat.com> - 1.0.8-3
- Fix sabayon remove

* Mon Jan 25 2010 Dan Walsh <dwalsh@redhat.com> - 1.0.8-2
- Fix sabayon installation

* Wed Nov 25 2009 Dan Walsh <dwalsh@redhat.com> - 1.0.8-1
- Fix sabayon file

* Wed Aug 26 2009 Dan Walsh <dwalsh@redhat.com> - 1.0.7-7
- Switch to use policycoreutils-sandbox init script

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jun 23 2009 Dan Walsh <dwalsh@redhat.com> - 1.0.7-5
- Changed to require policycoreutils-python

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 30 2009 Dan Walsh <dwalsh@redhat.com> - 1.0.7-1
- Change xguest init script to have proper summary

* Thu Jan 22 2009 Dan Walsh <dwalsh@redhat.com> - 1.0.6-8
- Modify xguest to be able to be installed in a livecd

* Fri Apr 4 2008 Dan Walsh <dwalsh@redhat.com> - 1.0.6-7
- Require newer version of policy

* Wed Mar 19 2008 Dan Walsh <dwalsh@redhat.com> - 1.0.6-6
- Change gecos field to say "Guest"

* Wed Feb 27 2008 Dan Walsh <dwalsh@redhat.com> - 1.0.6-5
- Leave xguest_u assignment on preun and always set the user to xguest_u on install

* Mon Feb 11 2008 Florian La Roche <laroche@redhat.com> - 1.0.6-4
- fix post requires on pam

* Thu Jan 31 2008 Dan Walsh <dwalsh@redhat.com> - 1.0.6-3
- Add support for exclusive login for xguest

* Tue Dec 18 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.6-2
- Remove lines from namespace.init on package removal

* Mon Dec 17 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.6-1
- Remove xguest init.d script on uninstall
- Fix description


* Fri Dec 7 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.5-2
- Turn on the xguest booleans

* Fri Dec 7 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.5-1
- Allow xguest to run nm-applet

* Tue Nov 27 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.4-2
- Fix permissions on /etc/init.d/xguest

* Wed Nov 21 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.4-1
- Add mount code to allow sharing of file system so hal and automount will work.
- I have added an initscript to set the / as shared and /tmp, /var/tmp and /home/xguest as private

* Fri Oct 26 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.3-1
- Remove exit lines
- Add LICENSE

* Mon Oct 22 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.2-1
- Cleanup spec file

* Mon Oct 22 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.1-2
- Turn on allow_polyinstantiation boolean

* Fri Oct 12 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.1-1
- Add sabayon support

* Thu Sep 13 2007 Dan Walsh <dwalsh@redhat.com> - 1.0.0-1
- Initial version
