
# 🧹 ComfyUI Cleaner

**Speed up your ComfyUI startup and reduce memory overhead by disabling unused custom nodes.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Have you ever installed dozens of custom node extensions only to forget which ones you actually use? ComfyUI Cleaner scans your workflow JSON files, identifies every node type you've ever used, and cross-references them with your installed extensions. It then helps you move unused extensions to a backup folder, keeping your ComfyUI lean and fast.

## ✨ Features

- **Intelligence**: Scans all `.json` workflows in your `user/workflows` directory.
- **Source-Aware**: Doesn't just look at folder names; it scans the extension's source code (`.py`, `.js`) to find node definitions.
- **Safe**: Moves extensions to a `custom_nodes_backup` folder instead of deleting them. You can restore them instantly.
- **Always-Keep List**: Automatically ignores essential extensions like ComfyUI-Manager and Custom-Scripts.
- **Fast**: Analyzes hundreds of nodes and extensions in seconds.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher.
- A ComfyUI installation.

### Installation

1. Clone this repository or download `clean_comfyui.py`.
2. Place the script in your main ComfyUI folder (the one containing `main.py`).

### Usage

**1. Dry Run (See what would be removed)**
```bash
python clean_comfyui.py
```

**2. Backup Unused Nodes**
```bash
python clean_comfyui.py --backup
```

**3. Specify ComfyUI Path (If running from elsewhere)**
```bash
python clean_comfyui.py --root "C:/Path/To/ComfyUI" --backup
```

## 🛠️ How it Works

1. **Workflow Analysis**: The script recursively scans your workflow directories to build a unique list of every used `node_type` (e.g., `KSampler`, `FaceDetailer`).
2. **Extension Mapping**: It iterates through every folder in `custom_nodes` and searches its files for those node type strings.
3. **Redundancy Detection**: If an extension doesn't contain any strings matching your used nodes, it's marked as unused.
4. **Cleanup**: Unused extensions are moved out of the active loading directory, so ComfyUI doesn't waste time importing them.

## ⚠️ Disclaimer

This tool moves files on your system. While it uses a "backup" approach, always ensure you have a fallback of your important data. The author is not responsible for any issues arising from the use of this script.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
