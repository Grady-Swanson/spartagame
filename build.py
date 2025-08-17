#!/usr/bin/env python3
"""
Build script for Catastrophe Civ web deployment
"""
import subprocess
import sys
import os

def build_web():
    """Build the game for web deployment using pygbag"""
    print("🎮 Building Catastrophe Civ for web...")
    
    try:
        # Build with pygbag
        cmd = [
            sys.executable, "-m", "pygbag",
            "main.py",
            "--width", "640",
            "--height", "360", 
            "--name", "Catastrophe Civ",
            "--archive"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        
        print("✅ Build successful!")
        print("📁 Built files are in the 'dist' directory")
        print("🌐 Ready for Vercel deployment!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_web()
