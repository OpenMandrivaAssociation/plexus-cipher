Name:		plexus-cipher
Version:	2.1.0
Release:	1
Summary:	Plexus encryption and decryption component
Group:		Development/Java
License:	ASL 2.0
URL:		https://github.com/codehaus-plexus/plexus-cipher
Source0:	https://github.com/codehaus-plexus/plexus-cipher/archive/refs/tags/plexus-cipher-%{version}.tar.gz#/plexus-cipher-%{version}.tar.gz
# Gradle 9.9.1 strictly pins org.codehaus.plexus:plexus-cipher 2.0.
Source1:	https://github.com/codehaus-plexus/plexus-cipher/archive/refs/tags/plexus-cipher-2.0.tar.gz#/plexus-cipher-2.0.tar.gz
BuildArch:	noarch

BuildRequires:	python
BuildRequires:	mvn(javax.inject:javax.inject)
BuildRequires:	mvn(org.eclipse.sisu:org.eclipse.sisu.inject)
BuildRequires:	java-current-devel
BuildRequires:	sysjar

%description
Plexus Cipher encrypts and decrypts passwords stored in Maven
settings. Maven components load the default implementation through
Sisu. 2.1.0 derives the AES key with PBKDF2WithHmacSHA1 for 310000
iterations and encodes the payload with java.util.Base64. Gradle 9.9.1
strictly pins 2.0, so that jar is installed beside 2.1.0. The 2.0 jar
still stretches the passphrase with SHA-256 for 1000 iterations.

%prep
%autosetup -n plexus-cipher-plexus-cipher-%{version}
%setup -q -T -D -a 1 -n plexus-cipher-plexus-cipher-%{version}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
set -- %{_javadir}/org.eclipse.sisu.inject-*.jar
SISU=$1
test -f "$SISU"
CP="%{_javadir}/atinject.jar:${SISU}"

write_index() {
	CIPHER_ROOT=$1 python - << 'PY'
import os
import re
from pathlib import Path
root = Path(os.environ["CIPHER_ROOT"]) / "src/main/java"
names = []
decl = re.compile(
    r"(?m)^(?:public\s+|protected\s+|private\s+)?(?:static\s+)?"
    r"(?:final\s+|abstract\s+|sealed\s+)?(?:class|interface|enum)\s+([A-Za-z0-9_]+)"
)
for path in sorted(root.rglob("*.java")):
    text = path.read_text(encoding="utf-8", errors="replace")
    match = decl.search(text)
    if not match or "@Named" not in text[:match.start()]:
        continue
    package = re.search(r"(?m)^package\s+([A-Za-z0-9_.]+)\s*;", text)
    if package:
        names.append(package.group(1) + "." + match.group(1))
if not names:
    raise SystemExit("no @Named classes found for the Sisu index")
dest = Path(os.environ["CIPHER_ROOT"]) / "src/main/resources/META-INF/sisu"
dest.mkdir(parents=True, exist_ok=True)
(dest / "javax.inject.Named").write_text("\n".join(names) + "\n", encoding="utf-8")
PY
}

compile_one() {
	root=$1
	ver=$2
	out=$3
	count=$4
	write_index "$root"
	find "$root/src/main/java" -name '*.java' > "$out.list"
	test "$(wc -l < "$out.list")" -eq "$count"
	mkdir -p "$out/classes"
	javac --release 8 -encoding UTF-8 -cp "$CP" -d "$out/classes" @"$out.list"
	/bin/cp -a "$root/src/main/resources/." "$out/classes/"
	jar cf "$out/plexus-cipher.jar" -C "$out/classes" .
	cat > "$out/plexus-cipher.pom" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.codehaus.plexus</groupId>
  <artifactId>plexus-cipher</artifactId>
  <version>${ver}</version>
  <name>Plexus Cipher</name>
  <description>Plexus encryption and decryption component.</description>
  <url>https://github.com/codehaus-plexus/plexus-cipher</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>javax.inject</groupId>
      <artifactId>javax.inject</artifactId>
      <version>1</version>
    </dependency>
  </dependencies>
</project>
EOF
}

compile_one . %{version} out21 4
compile_one plexus-cipher-plexus-cipher-2.0 2.0 out20 5

%install
sysjar install --buildroot %{buildroot} \
	--artifact out20/plexus-cipher.pom:out20/plexus-cipher.jar \
	--file-name plexus-cipher-2.0 \
	--alias org.sonatype.plexus:plexus-cipher \
	--filelist .mfiles20
/bin/mv %{buildroot}/usr/share/sysjar/index/org.codehaus.plexus/plexus-cipher.sysjar \
	%{buildroot}/usr/share/sysjar/index/org.codehaus.plexus/plexus-cipher-2.0.sysjar
sed -i 's|/usr/share/sysjar/index/org.codehaus.plexus/plexus-cipher\.sysjar|/usr/share/sysjar/index/org.codehaus.plexus/plexus-cipher-2.0.sysjar|' .mfiles20
if [ -f %{buildroot}/usr/share/sysjar/index/org.sonatype.plexus/plexus-cipher.sysjar ]; then
	/bin/mv %{buildroot}/usr/share/sysjar/index/org.sonatype.plexus/plexus-cipher.sysjar \
		%{buildroot}/usr/share/sysjar/index/org.sonatype.plexus/plexus-cipher-2.0.sysjar
	sed -i 's|/usr/share/sysjar/index/org.sonatype.plexus/plexus-cipher\.sysjar|/usr/share/sysjar/index/org.sonatype.plexus/plexus-cipher-2.0.sysjar|' .mfiles20
fi
sysjar install --buildroot %{buildroot} \
	--artifact out21/plexus-cipher.pom:out21/plexus-cipher.jar \
	--file-name plexus-cipher \
	--alias org.sonatype.plexus:plexus-cipher \
	--filelist .mfiles21
awk '!seen[$0]++' .mfiles20 .mfiles21 > .mfiles

%check
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
cat > Smoke.java << 'EOF'
import org.sonatype.plexus.components.cipher.DefaultPlexusCipher;
public class Smoke {
	public static void main(String[] args) throws Exception {
		DefaultPlexusCipher cipher = new DefaultPlexusCipher();
		String enc = cipher.encryptAndDecorate("gradle", "pin");
		String dec = cipher.decryptDecorated(enc, "pin");
		if (!"gradle".equals(dec)) {
			throw new RuntimeException(dec);
		}
		System.out.println(args[0] + " " + cipher.isEncryptedString(enc));
	}
}
EOF
mkdir -p check21 check20
javac --release 8 -encoding UTF-8 -cp %{buildroot}%{_javadir}/plexus-cipher.jar -d check21 Smoke.java
java -cp "check21:%{buildroot}%{_javadir}/plexus-cipher.jar" Smoke cipher21_ok > check21.txt
cat check21.txt
grep -F -q 'cipher21_ok true' check21.txt
javac --release 8 -encoding UTF-8 -cp %{buildroot}%{_javadir}/plexus-cipher-2.0.jar -d check20 Smoke.java
java -cp "check20:%{buildroot}%{_javadir}/plexus-cipher-2.0.jar" Smoke cipher20_ok > check20.txt
cat check20.txt
grep -F -q 'cipher20_ok true' check20.txt

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt README.md
