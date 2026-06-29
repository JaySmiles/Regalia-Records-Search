import os
import sys
import re
import urllib.request
import subprocess
import shutil

# 1. Set environment variables
os.environ["ANDROID_HOME"] = r"C:\Users\joshu\android-sdk"

# Determine path helper
repo_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_dir)

# 2. Run npm install
print("Installing npm dependencies...")
subprocess.run("npm install", shell=True, check=True)

# 3. Bundle XLSX library offline
xlsx_url = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"
xlsx_path = os.path.join("www", "xlsx.full.min.js")
print(f"Downloading XLSX offline bundle...")
try:
    urllib.request.urlretrieve(xlsx_url, xlsx_path)
    print("XLSX library downloaded successfully.")
except Exception as e:
    print(f"Warning: Failed to download XLSX library: {e}")

# 4. Remove Google Fonts link in www/index.html
index_path = os.path.join("www", "index.html")
print("Removing Google Fonts dependency...")
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()
# Regex replace the link tag
html_cleaned = re.sub(r'<link href="https://fonts.googleapis.com[^"]*">', '', html)
with open(index_path, "w", encoding="utf-8") as f:
    f.write(html_cleaned)

# 5. Add Android platform if it doesn't exist
if not os.path.exists(os.path.join("android", "app", "build.gradle")):
    if os.path.exists("android"):
        try:
            shutil.rmtree("android")
        except Exception:
            pass
    print("Adding Android platform...")
    subprocess.run("npx cap add android", shell=True, check=True)
else:
    print("Android platform already exists.")

# 6. Parse, increment, and update version in index.html and Gradle
print("Incrementing version and syncing to HTML/Gradle...")
with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()
m = re.search(r'v(\d+)\.(\d+)\.(\d+)', content)
if not m:
    print("Error: Could not find version pattern (vX.Y.Z) in index.html")
    sys.exit(1)

major = int(m.group(1))
minor = int(m.group(2))
patch = int(m.group(3))

# Increment patch version
new_patch = patch + 1
new_version_name = f"{major}.{minor}.{new_patch}"
new_version_code = major * 10000 + minor * 100 + new_patch

# Update HTML content with new version
updated_content = re.sub(r'v\d+\.\d+\.\d+', f'v{new_version_name}', content)
with open(index_path, "w", encoding="utf-8") as f:
    f.write(updated_content)

print(f"Bumped Version: {new_version_name} (Code: {new_version_code})")

# Use these for building
version_name = new_version_name
version_code = new_version_code

gradle_path = os.path.join("android", "app", "build.gradle")
with open(gradle_path, "r", encoding="utf-8") as f:
    gradle = f.read()

# Replace versionCode and versionName
gradle = re.sub(r'versionCode \d+', f'versionCode {version_code}', gradle)
gradle = re.sub(r'versionName "[^"]*"', f'versionName "{version_name}"', gradle)

# Disable minification & shrinking
gradle = gradle.replace("minifyEnabled true", "minifyEnabled false")
gradle = gradle.replace("shrinkResources true", "shrinkResources false")

with open(gradle_path, "w", encoding="utf-8") as f:
    f.write(gradle)

# 7. Sync Capacitor android
print("Syncing Capacitor android...")
subprocess.run("npx cap sync android", shell=True, check=True)

# 8. Set App Name
strings_xml_path = os.path.join("android", "app", "src", "main", "res", "values", "strings.xml")
with open(strings_xml_path, "r", encoding="utf-8") as f:
    strings_xml = f.read()
strings_xml = re.sub(r'<string name="app_name">.*</string>', '<string name="app_name">Regalia Records Search</string>', strings_xml)
with open(strings_xml_path, "w", encoding="utf-8") as f:
    f.write(strings_xml)
print("App name set to 'Regalia Records Search' in strings.xml")

# 9. Generate custom mipmap launcher icons using Pillow
print("Generating custom launcher icons using Pillow...")
try:
    from PIL import Image
    sizes = {'mipmap-mdpi':48,'mipmap-hdpi':72,'mipmap-xhdpi':96,'mipmap-xxhdpi':144,'mipmap-xxxhdpi':192}
    img = Image.open('www/icon-512.png').convert('RGBA')
    for folder, size in sizes.items():
        path = os.path.join('android', 'app', 'src', 'main', 'res', folder)
        os.makedirs(path, exist_ok=True)
        bg = Image.new('RGBA', (size,size), (14,15,17,255))
        resized_img = img.resize((size,size), Image.Resampling.LANCZOS)
        bg.paste(resized_img, (0,0), resized_img)
        out = bg.convert('RGB')
        out.save(os.path.join(path, 'ic_launcher.png'))
        out.save(os.path.join(path, 'ic_launcher_round.png'))
        out.save(os.path.join(path, 'ic_launcher_foreground.png'))
    print("Launcher icons generated successfully.")
except Exception as e:
    print(f"Warning: Failed to generate custom icons: {e}. Running pip install Pillow...")
    subprocess.run("pip install Pillow -q", shell=True)
    from PIL import Image
    sizes = {'mipmap-mdpi':48,'mipmap-hdpi':72,'mipmap-xhdpi':96,'mipmap-xxhdpi':144,'mipmap-xxxhdpi':192}
    img = Image.open('www/icon-512.png').convert('RGBA')
    for folder, size in sizes.items():
        path = os.path.join('android', 'app', 'src', 'main', 'res', folder)
        os.makedirs(path, exist_ok=True)
        bg = Image.new('RGBA', (size,size), (14,15,17,255))
        resized_img = img.resize((size,size), Image.Resampling.LANCZOS)
        bg.paste(resized_img, (0,0), resized_img)
        out = bg.convert('RGB')
        out.save(os.path.join(path, 'ic_launcher.png'))
        out.save(os.path.join(path, 'ic_launcher_round.png'))
        out.save(os.path.join(path, 'ic_launcher_foreground.png'))
    print("Launcher icons generated successfully after installation.")

# 10. Add storage permissions to AndroidManifest.xml
manifest_path = os.path.join("android", "app", "src", "main", "AndroidManifest.xml")
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = f.read()

perm_str = '<uses-permission android:name="android.permission.INTERNET" />'
new_perms = '<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />\n    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="29" />'
if 'READ_EXTERNAL_STORAGE' not in manifest:
    manifest = manifest.replace(perm_str, new_perms)
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest)
    print("Added storage permissions to AndroidManifest.xml")

# 11. Compile signed release APK
print("Compiling release APK...")
keystore_path = os.path.abspath("regalia.keystore")
os.chdir("android")
cmd = [
    "cmd.exe", "/c", "gradlew.bat", "assembleRelease",
    f"-Pandroid.injected.signing.store.file={keystore_path}",
    "-Pandroid.injected.signing.store.password=regaliakey123",
    "-Pandroid.injected.signing.key.alias=regalia",
    "-Pandroid.injected.signing.key.password=regaliakey123"
]
subprocess.run(cmd, check=True)

# 12. Copy output APK to Apks directory
os.chdir(repo_dir)

# Get custom description from command line arguments or fallback to git commit message
desc = ""
if len(sys.argv) > 1:
    desc = sys.argv[1].strip()
else:
    try:
        git_desc = subprocess.check_output("git log -1 --pretty=%B", shell=True).decode("utf-8").strip()
        desc = git_desc.replace('\n', ' ').strip()
    except Exception:
        pass

# Sanitize description for filename
if desc:
    # Remove characters that are illegal in Windows filenames: \ / : * ? " < > |
    desc = re.sub(r'[\x00-\x1f\\/:*?"<>|]', '', desc)
    # limit length to avoid too long filename errors
    desc = desc[:80].strip()
    suffix = f" - {desc}"
else:
    suffix = ""

os.makedirs("Apks", exist_ok=True)
src_apk = os.path.join("android", "app", "build", "outputs", "apk", "release", "app-release.apk")
dest_apk = os.path.join("Apks", f"Regalia-Records-v{version_name}{suffix}.apk")
if os.path.exists(src_apk):
    shutil.copy(src_apk, dest_apk)
    print(f"BUILD SUCCESS! APK generated at: {dest_apk}")
else:
    print("Error: Could not find output APK.")
    sys.exit(1)
