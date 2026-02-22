# Desktop Neko 🐾

A minimal, lightweight, and interactive desktop pet written in Python using PySide6. Desktop Neko lives on top of your windows, reacts to your clicks, and even watches you work! 

![Neko Preview](./assets/neko_idle.png) *(Preview placeholder)*

## ✨ Features

- **Always With You**: Sits quietly in the bottom-right corner of your screen, always on top.
- **Interactive**: Give her a click to pet her! She loves the attention.
- **Chatty**: She'll occasionally say random things or greet you when you wake her up.
- **Active Window Tracking**: She watches what you're doing! 
  - Switch windows a few times while she's asleep, and she might peek with one eye.
  - Switch windows repeatedly while she's awake, and she'll get curious... or dizzy if you switch too fast! 🌀
- **Sleep Mode**: If you haven't interacted with her or changed windows in a while, she'll nod off to save resources.
- **Auto-Start**: Can be configured to launch automatically when Windows starts.
- **Lightweight**: Designed to use minimal CPU and memory.

## 🚀 Getting Started

### Option 1: Run from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/sobiswriter/Desktop-Neko.git
   cd Desktop-Neko
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The main dependency is `PySide6`, `winshell`, and `pywin32`)*
3. Run the application:
   ```bash
   python main.py
   ```

### Option 2: Pre-compiled Executable

If you don't want to mess with Python, simply download the latest release `.exe` and double-click it! No installation required.

## 🎨 Customizing Assets

Don't like the default pixel art? You can easily change how your Neko looks! 

Just replace the `.png` files in the `assets/` folder with your own images. The script will automatically scale them to fit the `64x64` requirement. 
- `neko_idle.png`
- `neko_sleep.png`
- `neko_happy.png`
- `neko_peek.png`
- `neko_curious.png`
- `neko_agitated.png`

## 🛠️ Tech Stack

- **Language:** Python
- **GUI Framework:** PySide6
- **Window Management:** `win32gui`

## 📜 License

This project is open-source and available under the MIT License. Built by Sobi who kinda likes Nekos.