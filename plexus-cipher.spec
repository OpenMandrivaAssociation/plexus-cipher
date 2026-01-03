Name:           plexus-cipher
Version:        2.0
Release:        1
Summary:        Plexus encryption/decryption component
License:        Apache-2.0
URL:            https://github.com/codehaus-plexus/plexus-cipher
BuildArch:      noarch

Source0:        %{url}/archive/%{name}-%{version}/%{name}-%{version}.tar.gz

BuildRequires:  javapackages-bootstrap

%description
Plexus Cipher is a Java-based library from the Plexus project,
primarily used by Apache Maven to encrypt and decrypt sensitive data
in configuration files, such as passwords stored in settings.xml.
It enables developers to securely store encrypted credentials instead
of plain-text secrets when accessing Maven repositories or other
protected services.

%prep
%autosetup -p1 -C
%mvn_file : plexus/%{name}
%mvn_alias org.codehaus.plexus: org.sonatype.plexus:

%build
%mvn_build -j -- -DjavaVersion=8

%install
%mvn_install

%files -f .mfiles
%license LICENSE.txt NOTICE.txt
