Name:		plexus-cipher
Version:	2.0
Release:	2
Summary:	Plexus encryption and decryption component
Group:		Development/Java
License:	ASL 2.0
URL:		https://github.com/codehaus-plexus/plexus-cipher
Source0:	https://github.com/codehaus-plexus/plexus-cipher/archive/refs/tags/plexus-cipher-%{version}.tar.gz#/plexus-cipher-%{version}.tar.gz
BuildArch:	noarch

BuildRequires:	python
BuildRequires:	mvn(org.codehaus.plexus:plexus:pom::)
BuildRequires:	mvn(javax.inject:javax.inject)
# @Typed is provided scope. The sources import it.
BuildRequires:	mvn(org.eclipse.sisu:org.eclipse.sisu.inject)
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
# Older Maven artifacts used the Sonatype group id.
BuildOption(install):	--file-name %{name} --alias org.sonatype.plexus:plexus-cipher

%description
Plexus Cipher encrypts and decrypts passwords stored in Maven
settings. Maven components load the default implementation through
Sisu.

%prep
%autosetup -n plexus-cipher-plexus-cipher-%{version}
# Sisu loads @Named classes from this index. The indexer plugin is not packaged.
# The declaration has to start a line: the javadoc contains the word class.
python - <<'PY'
import re
from pathlib import Path
root = Path("src/main/java")
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
dest = Path("src/main/resources/META-INF/sisu")
dest.mkdir(parents=True, exist_ok=True)
(dest / "javax.inject.Named").write_text("\n".join(names) + "\n", encoding="utf-8")
PY

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt README.md
