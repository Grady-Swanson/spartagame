#!/usr/bin/env python3
"""
Build script for Catastrophe Civ web deployment
"""
import subprocess
import sys
import os
import shutil

def build_web():
    """Build static web deployment files"""
    print("🎮 Building Catastrophe Civ for web...")
    
    # Create dist directory
    os.makedirs("dist", exist_ok=True)
    
    try:
        # Copy game assets
        print("📁 Copying game assets...")
        
        # Copy main files
        if os.path.exists("main.py"):
            shutil.copy2("main.py", "dist/")
            print("✅ Copied main.py")
            
        if os.path.exists("background.png"):
            shutil.copy2("background.png", "dist/")
            print("✅ Copied background.png")
            
        # Copy Assets directory
        if os.path.exists("Assets"):
            if os.path.exists("dist/Assets"):
                shutil.rmtree("dist/Assets")
            shutil.copytree("Assets", "dist/Assets")
            print("Copied Assets directory")
        
        # Create web-friendly index.html
        index_path = os.path.join("dist", "index.html")
        print("Creating index.html...")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Catastrophe Civ</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #1e3c72, #2a5298); 
            color: white; 
            font-family: 'Arial', sans-serif; 
            text-align: center;
            min-height: 100vh;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .game-info {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .download-btn {
            background: #4CAF50;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        .download-btn:hover {
            background: #45a049;
        }
        .screenshot {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Catastrophe Civ</h1>
        <p>A fast-paced disaster survival town management game</p>
        
        <div class="game-info">
            <h2>About the Game</h2>
            <p>Build your town and help villagers with their problems before disaster strikes! You have exactly 60 seconds to assist as many NPCs as possible before one of four random disasters destroys your city.</p>
            
            <h3>Features</h3>
            <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
                <li>60-second gameplay rounds</li>
                <li>Randomized town layouts each game</li>
                <li>Interactive NPCs with problems to solve</li>
                <li>4 different disaster endings</li>
                <li>Building placement system</li>
                <li>Special character interactions</li>
            </ul>
        </div>
        
        <div class="game-info">
            <h2>How to Play</h2>
            <p>This is a desktop game built with Python and Pygame. Download and run locally for the best experience!</p>
            
            <a href="https://github.com/Grady-Swanson/spartagame" class="download-btn">
                Download Game
            </a>
            
            <p><strong>Requirements:</strong> Python 3.8+ and Pygame</p>
            <p><strong>Install:</strong> <code>pip install pygame</code></p>
            <p><strong>Run:</strong> <code>python main.py</code></p>
        </div>
        
        <div class="game-info">
            <h2>Controls</h2>
            <ul style="text-align: left; max-width: 300px; margin: 0 auto;">
                <li><strong>Mouse:</strong> Click to interact</li>
                <li><strong>F12:</strong> Toggle debug mode</li>
                <li><strong>ESC:</strong> Return to menu</li>
                <li><strong>R:</strong> Restart</li>
            </ul>
        </div>
        
        <p style="margin-top: 40px;">
            <a href="https://github.com/Grady-Swanson/spartagame" style="color: #64b5f6;">View Source Code on GitHub</a>
        </p>
    </div>
</body>
</html>""")
        
        print("Static deployment ready!")
        print("Ready for Vercel deployment!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_web()
