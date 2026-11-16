"""Holt Forge für das Docker-Image: vorhandene Installation oder Installer (forge-installer-….jar) aus ./forge übernehmen,
sonst die neueste Version von GitHub laden (Archiv .tar.bz2 oder Installer).
Aufruf: python3 fetch_forge.py QUELLORDNER ZIELORDNER [VERSION|latest]"""
import glob, hashlib, json, os, re, shutil, subprocess, sys, tarfile, tempfile, urllib.request

JAR = "forge-gui-desktop-*-jar-with-dependencies.jar"
API = "https://api.github.com/repos/Card-Forge/forge/releases"


def find_root(base):
    for root, _dirs, _files in os.walk(base):
        if glob.glob(os.path.join(root, JAR)):
            return root
    return None


def run_installer(jar, dest):
    """Forge-Installer (IzPack) unbeaufsichtigt ausführen."""
    print(f"Installiere Forge mit {os.path.basename(jar)} nach {dest} ...", flush=True)
    opts = os.path.join(tempfile.mkdtemp(), "forge.properties")
    with open(opts, "w") as f:
        f.write(f"INSTALL_PATH={os.path.abspath(dest)}\n")
    r = subprocess.run(["java", "-jar", jar, "-options", opts], capture_output=True, text=True, timeout=1800)
    if r.returncode != 0 or not glob.glob(os.path.join(dest, JAR)):
        sys.exit("Forge-Installer fehlgeschlagen:\n" + (r.stdout + r.stderr)[-1500:])


def get(url, accept="application/octet-stream"):
    req = urllib.request.Request(url, headers={"User-Agent": "commander-db-docker", "Accept": accept})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def from_github(version, dest):
    rel = json.loads(get(f"{API}/latest" if version in ("", "latest") else f"{API}/tags/forge-{version}", "application/json"))
    assets = {a["name"]: a["browser_download_url"] for a in rel.get("assets", [])}
    tars = sorted(n for n in assets if re.match(r"forge-gui-desktop-.*\.tar\.bz2$", n))
    installers = sorted(n for n in assets if re.match(r"forge-installer-.*\.jar$", n))
    if not tars and installers:
        print(f"Lade {installers[-1]} aus Release {rel.get('tag_name')} ...", flush=True)
        path = os.path.join(tempfile.mkdtemp(), installers[-1])
        with open(path, "wb") as f:
            f.write(get(assets[installers[-1]]))
        run_installer(path, dest)
        return
    if not tars:
        sys.exit(f"Im Forge-Release {rel.get('tag_name')} gibt es kein forge-gui-desktop-….tar.bz2.\n"
                 "Bitte eine vorhandene Forge-Installation in den Ordner ./forge kopieren und neu bauen.")
    name = tars[-1]
    print(f"Lade {name} aus Release {rel.get('tag_name')} ...", flush=True)
    data = get(assets[name])
    sha_name = next((n for n in assets if n.startswith(name) and n.lower().endswith(("sha256", ".sha"))), None)
    if sha_name:
        expected = get(assets[sha_name]).decode().split()[0].lower()
        actual = hashlib.sha256(data).hexdigest()
        if expected != actual:
            sys.exit(f"Prüfsumme stimmt nicht ({actual} statt {expected}) – Abbruch.")
        print("Prüfsumme in Ordnung.")
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, name)
    open(path, "wb").write(data)
    with tarfile.open(path, "r:bz2") as t:
        t.extractall(os.path.join(tmp, "x"), filter="data")
    root = find_root(os.path.join(tmp, "x"))
    if not root:
        sys.exit("Im Forge-Archiv wurde keine forge-gui-desktop-…jar gefunden.")
    shutil.copytree(root, dest, dirs_exist_ok=True)
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    src, dest = sys.argv[1], sys.argv[2]
    version = sys.argv[3] if len(sys.argv) > 3 else "latest"
    os.makedirs(dest, exist_ok=True)
    root = find_root(src) if os.path.isdir(src) else None
    inst = sorted(glob.glob(os.path.join(src, "**", "forge-installer-*.jar"), recursive=True)) if os.path.isdir(src) else []
    if not root and inst:
        run_installer(inst[-1], dest)
    elif root:
        print(f"Verwende mitgelieferte Forge-Installation aus {root}")
        shutil.copytree(root, dest, dirs_exist_ok=True)
    else:
        try:
            from_github(version, dest)
        except SystemExit:
            raise
        except Exception as e:
            sys.exit(f"Forge konnte nicht von GitHub geladen werden ({e}).\n"
                     "Abhilfe: eine vorhandene Forge-Installation in den Ordner ./forge kopieren und neu bauen.")
    jars = glob.glob(os.path.join(dest, JAR))
    if not jars or not os.path.isdir(os.path.join(dest, "res")):
        sys.exit("Forge unvollständig: jar-Datei oder Ordner res fehlt.")
    print("Forge bereit:", os.path.basename(jars[0]))


if __name__ == "__main__":
    main()
