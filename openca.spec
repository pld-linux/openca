# TODO:
# - remove all that crazy finding...
# - make it build
Summary:	OpenCA - Open Certificate Authority
Summary(pl):	OpenCA - otwarty projekt CA
%define		realname	OpenCA
Name:		openca
Version:	0.9.2.5
Release:	0.1
Epoch:		2
License:	BSD
Group:		Applications/Publishing/SGML
Source0:	http://dl.sourceforge.net/openca/%{name}-%{version}.tar.gz
# Source0-md5:	8181ba08016f8c12a91707e61601cd8d
Patch0:		%{name}-install.patch
BuildRequires:	libiconv-devel
BuildRequires:	openssl-devel
BuildRequires:	perl-XML-Parser >= 2.23
URL:		http://www.openca.org/openca/
BuildRequires:	openldap-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define ossl_cnf	/etc/openssl/openssl.cnf
%define ossl_country	%(grep '^countryName_default.*=.' %{ossl_cnf}| sed -e 's|^countryName_default.*=.||g' )
%define ossl_state	%(grep '^stateOrProvinceName_default.*=.' %{ossl_cnf}| sed -e 's|^stateOrProvinceName_default.*=.||g' )

%{!?securehost:	%define securehost	secure.%(hostname -d) }
%{!?caorg:	%define caorg		%(hostname -d|sed -e 's/\(.*\)\..*$/\1/g') }
%{!?cacountry:	%define cacountry	%{ossl_country} }
%{!?castate:	%define castate		%{ossl_state} }

%description
The OpenCA PKI Development Project is a collaborative effort to
develop a robust, full-featured and Open Source out-of-the-box
Certification Authority implementing the most used protocols with
full-strength cryptography world-wide. OpenCA is based on many
Open-Source Projects. Among the supported software is OpenLDAP,
OpenSSL, Apache Project, Apache mod_ssl.

%description -l pl
Projekt OpenCA PKI Development to wspólne próby stworzenia potê¿nego,
w pe³ni funkcjonalnego, dzia³aj±cego od razu po instalacji CA
(Certificate Authority) o otwartych ¼ród³ach z implementacj± wiêkszo¶ci 
u¿ywanych protoko³ów oraz pe³n± siln± kryptografi± dostêpn± dla ca³ego 
¶wiata. OpenCA jest oparte na wielu projektach Open Source. W¶ród 
wspieranego oprogramowania s± OpenLDAP, OpenSSL, projekt Apache, 
mod_ssl dla Apache.

%prep
%setup -q -n %{realname}-%{version}
%patch0 -p0
rm -rf src/modules/Convert-ASN1*
rm -rf src/modules/Digest-MD5*
rm -rf src/modules/IO-Socket-SSL*
rm -rf src/modules/MIME-Base64*
rm -rf src/modules/perl-ldap*
rm -rf src/modules/URI-*

%build
%configure \
	--with-prefix=%{_prefix} \
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

%{__make} install-ca \
	%{camakeins}

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
