%global debug_package %{nil}

Name:           acme-redirect
Version:        0.5.3
Release:        1%{?dist}
Summary:        ACME answerer & 80-to-443 redirector

License:        GPLv3
URL:            https://github.com/kpcyrd/acme-redirect
Source0:        https://github.com/kpcyrd/acme-redirect/archive/v%{version}.tar.gz

BuildRequires:  cargo make rust openssl-devel scdoc
Requires:       glibc libgcc openssl-libs

%description
Tiny http daemon that answers acme challenges and
redirects everything else to https

%prep
%autosetup

%build
cargo build --release
make docs

%install
# `install -D -t <dir>` does not correctly create `<dir>` on EL7
%if 0%{?el7}
    mkdir -p \
        %{buildroot}%{_bindir} \
        %{buildroot}%{_sysconfdir} \
        %{buildroot}%{_libdir}/systemd/system \
        %{buildroot}%{_mandir}/man{1,5}
%endif

install -Dm 755 -t %{buildroot}%{_bindir} target/release/acme-redirect
install -Dm 644 -t %{buildroot}%{_sysconfdir} contrib/confs/acme-redirect.conf
install -Dm 644 contrib/confs/certs.d/example.com.conf %{buildroot}%{_sysconfdir}/acme-redirect.d/example.com.conf.sample
install -Dm 644 -t %{buildroot}%{_libdir}/systemd/system \
    contrib/systemd/acme-redirect-renew.service \
    contrib/systemd/acme-redirect-renew.timer \
    contrib/systemd/acme-redirect.service

install -Dm 644 contrib/systemd/acme-redirect.sysusers %{buildroot}%{_libdir}/sysusers.d/acme-redirect.conf
install -Dm 644 contrib/systemd/acme-redirect.tmpfiles %{buildroot}%{_libdir}/tmpfiles.d/acme-redirect.conf

install -Dm 644 -t %{buildroot}%{_mandir}/man1 contrib/docs/acme-redirect.1
install -Dm 644 -t %{buildroot}%{_mandir}/man5 \
    contrib/docs/acme-redirect.conf.5 \
    contrib/docs/acme-redirect.d.5

%post
systemd-sysusers
systemd-tmpfiles --create

%files
%{_bindir}/acme-redirect
%config(noreplace) %{_sysconfdir}/acme-redirect.conf
%config %{_sysconfdir}/acme-redirect.d/example.com.conf.sample
%{_libdir}/systemd/system/acme-redirect-renew.service
%{_libdir}/systemd/system/acme-redirect-renew.timer
%{_libdir}/systemd/system/acme-redirect.service
%{_libdir}/sysusers.d/acme-redirect.conf
%{_libdir}/tmpfiles.d/acme-redirect.conf
%{_mandir}/man1/acme-redirect.1.gz
%{_mandir}/man5/acme-redirect.conf.5.gz
%{_mandir}/man5/acme-redirect.d.5.gz
%license LICENSE
%doc README.md

%changelog
* Tue Apr 05 2022 cyqsimon - 0.5.3-1
- Fix "missing field `contact` at line 13 column 1" error caused by letsencrypt api response change
