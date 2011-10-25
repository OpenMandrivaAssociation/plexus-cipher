Name:           plexus-cipher
Version:        1.5
Release:        4
Summary:        Plexus Cipher: encryption/decryption Component

Group:          Development/Java
License:        ASL 2.0
URL:            http://spice.sonatype.org
#svn export http://svn.sonatype.org/spice/tags/plexus-cipher-1.5
#tar zcf plexus-cipher-1.5.tar.gz plexus-cipher-1.5
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch

BuildRequires: java-devel >= 0:1.6.0
BuildRequires: maven2
BuildRequires: maven-plugin-plugin
BuildRequires: maven-compiler-plugin
BuildRequires: maven-install-plugin
BuildRequires: maven-jar-plugin
BuildRequires: maven-javadoc-plugin
BuildRequires: maven-resources-plugin
BuildRequires: maven-surefire-maven-plugin
BuildRequires: maven-surefire-provider-junit
BuildRequires: maven-doxia-sitetools
BuildRequires: plexus-container-default
BuildRequires: forge-parent
BuildRequires: spice-parent
BuildRequires: plexus-maven-plugin
BuildRequires: junit
BuildRequires: maven-shared-reporting-impl
BuildRequires: plexus-digest

Requires: maven2
Requires:       jpackage-utils
Requires:       java
Requires(post):       jpackage-utils
Requires(postun):     jpackage-utils


%description
Plexus Cipher: encryption/decryption Component

%package javadoc
Group:          Development/Java
Summary:        Javadoc for %{name}
Requires:       jpackage-utils

%description javadoc
API documentation for %{name}.


%prep
%setup -q -n %{name}-%{version}

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mvn-jpp \
        -e \
        -Dmaven2.jpp.mode=true \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        install javadoc:javadoc

%install
rm -rf %{buildroot}

# jars
install -d -m 0755 %{buildroot}%{_javadir}/plexus
install -m 644 target/%{name}-%{version}.jar   %{buildroot}%{_javadir}/plexus

(cd %{buildroot}%{_javadir}/plexus && for jar in *-%{version}*; \
    do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

%add_to_maven_depmap org.sonatype.plexus %{name} %{version} JPP/plexus %{name}

# poms
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml \
    %{buildroot}%{_mavenpomdir}/JPP.plexus-%{name}.pom

# javadoc
install -d -m 0755 %{buildroot}%{_javadocdir}/plexus/%{name}-%{version}
cp -pr target/site/api*/* %{buildroot}%{_javadocdir}/plexus/%{name}-%{version}/
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/plexus/%{name}
rm -rf target/site/api*

%post
%update_maven_depmap

%postun
%update_maven_depmap

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_javadir}/plexus/*
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*
%doc NOTICE.txt

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/plexus/%{name}-%{version}
%{_javadocdir}/plexus/%{name}

