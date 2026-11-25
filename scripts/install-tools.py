"""Install official pinned CLI releases, checking upstream SHA256 manifests."""
import hashlib, io, pathlib, platform, tarfile, urllib.request, zipfile
TOOLS = [('rhysd/actionlint','v1.7.12','actionlint_1.7.12_{os}_amd64.tar.gz','actionlint_1.7.12_checksums.txt'),('terraform-linters/tflint','v0.66.0','tflint_{os}_amd64.zip','checksums.txt'),('gitleaks/gitleaks','v8.30.1','gitleaks_8.30.1_{os}_x64.tar.gz','gitleaks_8.30.1_checksums.txt')]
root=pathlib.Path('.tools'); root.mkdir(exist_ok=True)
for repo,version,asset,checksums in TOOLS:
    name=repo.split('/')[-1]
    if platform.system()=='Windows':
        asset={'actionlint':'actionlint_1.7.12_windows_amd64.zip','tflint':'tflint_windows_amd64.zip','gitleaks':'gitleaks_8.30.1_windows_x64.zip'}[name]
    else: asset=asset.format(os='linux')
    base=f'https://github.com/{repo}/releases/download/{version}/'
    data=urllib.request.urlopen(base+asset).read()
    manifest=urllib.request.urlopen(base+checksums).read().decode()
    line=next(line for line in manifest.splitlines() if line.split()[-1].lstrip('*')==asset)
    if hashlib.sha256(data).hexdigest()!=line.split()[0]: raise SystemExit('Checksum mismatch')
    binary=name+('.exe' if platform.system()=='Windows' else '')
    if asset.endswith('.zip'):
        z=zipfile.ZipFile(io.BytesIO(data)); content=z.read(next(n for n in z.namelist() if pathlib.PurePosixPath(n).name==binary))
    else:
        z=tarfile.open(fileobj=io.BytesIO(data)); content=z.extractfile(next(m for m in z.getmembers() if pathlib.PurePosixPath(m.name).name==binary)).read()
    (root/binary).write_bytes(content); (root/binary).chmod(0o755)
    print(name,version,'official checksum verified')
