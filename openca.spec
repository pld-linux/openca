Summary:	OpenCA - Open Certificate Authority
Name:		openca
%define post 7
%define rel 0.9.1
Version:	%{rel}.%{post}
Release:	0.1
Epoch:		2
License:	Free (Copyright (C) 1999 The OpenJade group)
Group:		Applications/Publishing/SGML
Source0:	http://dl.sourceforge.net/openca/%{name}-%{rel}-%{post}.tar.gz
# Source0-md5:	48796e666f24eb063feaa7c237f81adc
URL:		http://www.openca.org/openca/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Open Certificate Authority

%define ossl_cnf	/etc/openssl/openssl.cnf
%define ossl_country	%(grep '^countryName_default.*=.' %{ossl_cnf}| sed -e 's|^countryName_default.*=.||g' )
%define ossl_state	%(grep '^stateOrProvinceName_default.*=.' %{ossl_cnf}| sed -e 's|^stateOrProvinceName_default.*=.||g' )

%{!?securehost:			%define securehost	secure.%(hostname -d) }
%{!?caorg:			%define caorg		%(hostname -d|sed -e 's/\(.*\)\..*$/\1/g') }
%{!?cacountry:			%define cacountry	%{ossl_country} }
%{!?castate:			%define castate		%{ossl_state} }

%prep
%setup -q 
rm -rf src/modules/Convert-ASN1*
rm -rf src/modules/Digest-MD5*
rm -rf src/modules/IO-Socket-SSL*
rm -rf src/modules/MIME-Base64*
rm -rf src/modules/perl-ldap*
rm -rf src/modules/URI-*

%build
%configure --with-prefix=%{_prefix} \
	--with-hierarchy-level=ca \
	--with-etc-prefix=%{_sysconfdir} \
	--with-lib-prefix=%{_libdir} \
	--with-var-prefix=%{_vardir} \
	--with-httpd-fs-prefix=/home/services/httpd \
	--with-engine \
	--with-web-host=%{securehost} \
	--with-ca-organization="%{caorg}" \
	--with-ca-country=%{cacountry} \
	--with-ca-locality=%{castate} \
	--enable-engine=yes \
	--enable-ocspd \
	--enable-sendmail \
	--enable-dbi \
	--enable-rbac \
	--enable-dbis \
	--with-service-mail-account=ca@%{securehost} \
	--with-openca-user=root \
	--with-openca-group=root \
	--with-httpd-user=http \
	--with-httpd-group=http

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%define camakeins prefix="$RPM_BUILD_ROOT%{_prefix}" ca_htdocs_fs_prefix="$RPM_BUILD_ROOT/home/services/httpd/htdocs/ca" ca_cgi_fs_prefix="$RPM_BUILD_ROOT/home/services/httpd/cgi-bin/ca" ra_htdocs_fs_prefix="$RPM_BUILD_ROOT/home/services/httpd/htdocs/ra" ra_cgi_fs_prefix="$RPM_BUILD_ROOT/home/services/httpd/cgi-bin/ra" pub_htdocs_fs_prefix="$RPM_BUILD_ROOT/home/services/httpd/htdocs/pub" pub_cgi_fs_prefix="$RPM_BUILD_ROOT/home/services/httpd/cgi-bin/pub" scep_cgi_fs_prefix="$RPM_BUILD_ROOT/home/services/httpd/cgi-bin/scep" etc_prefix="$RPM_BUILD_ROOT%{_sysconfdir}" lib_prefix="$RPM_BUILD_ROOT%{_libdir}" var_prefix="$RPM_BUILD_ROOT%{_vardir}"

make %{camakeins} install-ca
rm -f %{_tmppath}/openca-ca.l*
find "$RPM_BUILD_ROOT" ! -type d >%{_tmppath}/openca-ca.list
find "$RPM_BUILD_ROOT" -type l >%{_tmppath}/openca-ca.lnks
cat %{_tmppath}/openca-ca.list|sed -e "s|$RPM_BUILD_ROOT||g" -e 's|\(.*man[0-9]/.*\)|\1.gz|g' >%{_tmppath}/openca-ca.list.out
cat %{_tmppath}/openca-ca.lnks|sed -e 's|\(.*man[0-9]/.*\)|\1.gz|g' >%{_tmppath}/openca-ca.lnks.out
for i in $(cat %{_tmppath}/openca-ca.lnks.out)
do
	REAL_PATH=$(ls -l "$i"|sed -e 's|.*->.\(.*\)$|\1|g'|sed -e "s|$RPM_BUILD_ROOT||g")
	ln -sf "$REAL_PATH" "$i"
done

%clean
rm -rf $RPM_BUILD_ROOT

%files -f /var/tmp/openca-ca.list.out
%defattr(644,root,root,755)
