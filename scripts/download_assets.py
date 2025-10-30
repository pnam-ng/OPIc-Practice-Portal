#!/usr/bin/env python3
"""
Download required CSS/JS assets for the OPIc Practice Portal
"""
import os
import sys
import urllib.request
import zipfile
import shutil

def download_file(url, destination):
    """Download a file from URL to destination"""
    print(f"Downloading: {url}")
    urllib.request.urlretrieve(url, destination)
    print(f"✓ Saved to: {destination}")

def extract_zip(zip_path, extract_to):
    """Extract a zip file"""
    print(f"Extracting: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✓ Extracted to: {extract_to}")

def setup_bootstrap():
    """Download and setup Bootstrap"""
    print("\n" + "="*60)
    print("Setting up Bootstrap 5.3.0")
    print("="*60)
    
    url = "https://github.com/twbs/bootstrap/releases/download/v5.3.0/bootstrap-5.3.0-dist.zip"
    temp_zip = "temp_bootstrap.zip"
    temp_dir = "temp_bootstrap"
    
    try:
        # Download
        download_file(url, temp_zip)
        
        # Extract
        extract_zip(temp_zip, temp_dir)
        
        # Copy CSS files
        css_src = os.path.join(temp_dir, "bootstrap-5.3.0-dist", "css")
        css_dest = os.path.join("static", "css")
        os.makedirs(css_dest, exist_ok=True)
        
        for file in ["bootstrap.min.css", "bootstrap.min.css.map"]:
            src = os.path.join(css_src, file)
            dest = os.path.join(css_dest, file)
            if os.path.exists(src):
                shutil.copy2(src, dest)
                print(f"✓ Copied: {file}")
        
        # Copy JS files
        js_src = os.path.join(temp_dir, "bootstrap-5.3.0-dist", "js")
        js_dest = os.path.join("static", "js")
        os.makedirs(js_dest, exist_ok=True)
        
        for file in ["bootstrap.bundle.min.js", "bootstrap.bundle.min.js.map"]:
            src = os.path.join(js_src, file)
            dest = os.path.join(js_dest, file)
            if os.path.exists(src):
                shutil.copy2(src, dest)
                print(f"✓ Copied: {file}")
        
        # Cleanup
        os.remove(temp_zip)
        shutil.rmtree(temp_dir)
        print("✓ Bootstrap setup complete!")
        
    except Exception as e:
        print(f"✗ Error setting up Bootstrap: {e}")
        return False
    
    return True

def setup_fontawesome():
    """Download and setup Font Awesome"""
    print("\n" + "="*60)
    print("Setting up Font Awesome 6.4.0")
    print("="*60)
    
    url = "https://use.fontawesome.com/releases/v6.4.0/fontawesome-free-6.4.0-web.zip"
    temp_zip = "temp_fontawesome.zip"
    temp_dir = "temp_fontawesome"
    
    try:
        # Download
        download_file(url, temp_zip)
        
        # Extract
        extract_zip(temp_zip, temp_dir)
        
        # Copy CSS files
        css_src = os.path.join(temp_dir, "fontawesome-free-6.4.0-web", "css")
        css_dest = os.path.join("static", "css")
        os.makedirs(css_dest, exist_ok=True)
        
        for file in ["all.min.css"]:
            src = os.path.join(css_src, file)
            dest = os.path.join(css_dest, file)
            if os.path.exists(src):
                shutil.copy2(src, dest)
                print(f"✓ Copied: {file}")
        
        # Copy webfonts directory
        webfonts_src = os.path.join(temp_dir, "fontawesome-free-6.4.0-web", "webfonts")
        webfonts_dest = os.path.join("static", "webfonts")
        
        if os.path.exists(webfonts_dest):
            shutil.rmtree(webfonts_dest)
        
        shutil.copytree(webfonts_src, webfonts_dest)
        print(f"✓ Copied webfonts directory")
        
        # Cleanup
        os.remove(temp_zip)
        shutil.rmtree(temp_dir)
        print("✓ Font Awesome setup complete!")
        
    except Exception as e:
        print(f"✗ Error setting up Font Awesome: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("="*60)
    print("OPIc Practice Portal - Asset Downloader")
    print("="*60)
    print("\nThis script will download:")
    print("  - Bootstrap 5.3.0 (CSS & JS)")
    print("  - Font Awesome 6.4.0 (CSS & Fonts)")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("static"):
        print("✗ Error: 'static' directory not found!")
        print("  Please run this script from the project root directory.")
        sys.exit(1)
    
    success = True
    
    # Setup Bootstrap
    if not setup_bootstrap():
        success = False
    
    # Setup Font Awesome
    if not setup_fontawesome():
        success = False
    
    if success:
        print("\n" + "="*60)
        print("✓ All assets downloaded successfully!")
        print("="*60)
        print("\nYou can now run the application:")
        print("  python app.py")
        print()
    else:
        print("\n" + "="*60)
        print("✗ Some assets failed to download")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()














