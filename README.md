# Roblox 2 Rojo

A tool to convert Roblox RBXL/RBXM files to Rojo project structure.

## Features

- **RBXL/RBXM to RBXLX/RBXMX Conversion**: Uses Lune's native parser for reliable conversion of both place and model files
- **Rojo Project Generation**: Automatically creates `default.project.json` with proper service mappings
- **Service Support**: Extracts from:
  - ServerScriptService
  - ReplicatedStorage
  - ServerStorage
  - StarterPlayer (including StarterPlayerScripts and StarterCharacterScripts)
  - StarterGui (with full GUI hierarchy and properties)
  - ReplicatedFirst
- **RemoteEvent Support**: Creates folders with `init.meta.json` for RemoteEvents and RemoteFunctions
- **Child Script Support**: Handles scripts with children by creating folders with `init.luau`, `init.server.luau`, or `init.client.luau`
- **GUI Support**: Exports ScreenGuis, Frames, TextLabels, and all UI elements with properties preserved in `init.meta.json` files


## Requirements

- Python 3.7 or higher
- [Lune](https://lune-org.github.io/docs) - for RBXL parsing


## Usage

1. Launch the application: `python3 main.py`
2. Click "Browse" to select your RBXL/RBXM file
3. Choose an output directory
4. Click "Convert to Rojo Project"
5. Your Rojo project will be generated with all scripts, GUIs, and RemoteEvents!

## Antivirus False Positives

### Why does my antivirus flag this as a virus?

This application may trigger false positive detections from antivirus software. This is a common issue with Python applications packaged into executables using tools like PyInstaller or similar bundlers. Here's why:

**Common Reasons for False Positives:**

1. **Unsigned Executable**: The Windows/Mac executable is not digitally signed with an expensive code signing certificate, which makes antivirus software suspicious

2. **PyInstaller/Bundler Signatures**: Packaging tools like PyInstaller are commonly used by both legitimate software and malware, so antivirus heuristics flag them as potentially dangerous

3. **Lune Auto-Installation**: The application automatically downloads and installs Lune runtime if not found, which involves:
   - Downloading executables from the internet
   - Writing to your home directory (`~/.rblx2rojo/lune`)
   - Making files executable
   
   These behaviors are legitimate but can trigger heuristic-based detection

4. **Low Distribution Numbers**: Newly released versions haven't been analyzed by enough antivirus vendors to be whitelisted

### Is this software safe?

Yes! This is completely open-source software. You can:

- **Review the source code**: All code is available in this repository
- **Build it yourself**: Run from source with `python3 main.py` instead of using the executable

## Limitations

- Requires Lune to be installed
- Only extracts from the target services (ServerScriptService, ReplicatedStorage, etc.)
- Some instance properties may not be preserved in the conversion



## License

MIT License - See LICENSE file for details.

You are free to use, modify, and distribute this software. Attribution is required if used in your projects.
