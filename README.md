# Catastrophe Civ

A fast-paced disaster survival town management game built with Pygame.

## 🎮 Game Description

Build your town and help villagers with their problems before disaster strikes! You have exactly 60 seconds to assist as many NPCs as possible before one of four random disasters destroys your city.

### Features
- 60-second gameplay rounds
- Randomized town layouts each game
- Interactive NPCs with problems to solve
- 4 different disaster endings
- Building placement system
- Special character interactions (like the Blacksmith's help requests)

## 🚀 Play Online

Visit [your-vercel-url.vercel.app](https://your-vercel-url.vercel.app) to play in your browser!

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd catastrophe-civ

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

### Building for Web
```bash
# Install pygbag if not already installed
pip install pygbag

# Build for web
python -m pygbag main.py --width 640 --height 360 --name "Catastrophe Civ"
```

## 🎯 Game Controls

- **Mouse**: Click to interact with NPCs and buildings
- **F12**: Toggle debug mode
- **ESC**: Return to menu
- **R**: Restart (when available)

### Debug Controls (F12 to enable)
- **L**: List all villagers
- **0-6**: Force exclamation on specific villager
- **X**: Random villager exclamation
- **E**: Force timer end

## 🏗️ Project Structure

```
├── main.py              # Main game file
├── Assets/              # Game assets
│   ├── Buildings/       # Building sprites
│   ├── Villagers/       # Character sprites
│   └── Speech/          # Speech bubble images
├── background.png       # Game background
└── requirements.txt     # Python dependencies
```

## 🚀 Deployment

This game is deployed on Vercel using Pygbag to convert Pygame to WebAssembly.

## 📜 License

MIT License - see LICENSE file for details.