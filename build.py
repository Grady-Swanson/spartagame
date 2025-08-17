#!/usr/bin/env python3
"""
Build script for Catastrophe Civ web deployment
"""
import subprocess
import sys
import os
import shutil

def build_web():
    """Build the game for web deployment using pygbag"""
    print("🎮 Building Catastrophe Civ for web...")
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    try:
        # Build with pygbag
        cmd = [
            sys.executable, "-m", "pygbag",
            "main.py",
            "--width", "640",
            "--height", "360", 
            "--name", "Catastrophe Civ",
            "--archive",
            "--ume_block", "0"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Build successful!")
        
        # Copy built files to dist directory
        if os.path.exists("main"):
            for file in os.listdir("main"):
                src = os.path.join("main", file)
                dst = os.path.join("dist", file)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    print(f"📁 Copied {file} to dist/")
        
        # Create a simple index.html if pygbag didn't create one
        index_path = os.path.join("dist", "index.html")
        if not os.path.exists(index_path):
            print("📄 Creating index.html...")
            with open(index_path, "w") as f:
                f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Catastrophe Civ</title>
    <meta charset="utf-8">
    <style>
        body { margin: 0; padding: 20px; background: #222; color: white; font-family: Arial, sans-serif; text-align: center; }
        canvas { border: 2px solid #444; }
        .container { max-width: 800px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Catastrophe Civ</h1>
        <p>Loading game...</p>
        <canvas id="canvas" width="640" height="360"></canvas>
        <p>Click to start playing!</p>
    </div>
    <script src="main.js"></script>
</body>
</html>""")
        
        print("🌐 Ready for Vercel deployment!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_web()
