import PyInstaller.__main__
import os
import shutil

def build():
    # Cleanup previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    print("Building TeleKB...")
    
    PyInstaller.__main__.run([
        'main.py',
        '--name=TeleKB',
        '--onedir',       # Create a directory with the executable (easier for debugging)
        '--noconsole',    # Hide console window
        '--clean',
        # Add data files if needed. 
        # For example, if we had an icon: '--icon=resources/icon.ico'
        # To include a folder: '--add-data=resources;resources' (Windows: ;)
        
        # Hidden imports often needed for Tkinter or Database drivers if not detected
        '--hidden-import=sqlite3',
        '--hidden-import=tkinter',
        '--hidden-import=telethon',
        '--hidden-import=google.generativeai',
        
        # Exclude module: tk (no need to exclude standard lib usually, but just in case)
    ])
    
    print("Build complete.")
    
    # Post-build: Copy necessary files to dist/TeleKB
    dist_dir = os.path.join("dist", "TeleKB")
    
    files_to_copy = [
        ".env.template",
        "README_USER.txt"
    ]
    
    for f in files_to_copy:
        if os.path.exists(f):
            shutil.copy(f, dist_dir)
            print(f"Copied {f} to {dist_dir}")
        else:
            print(f"Warning: {f} not found.")
            
    # Copy output directory structure if needed (optional)
    # output_dir = os.path.join(dist_dir, "output")
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)
        
    print(f"Distribution package is ready at: {os.path.abspath(dist_dir)}")

if __name__ == "__main__":
    build()
