# Rblx 2 Rojo

A tool to convert Roblox RBXL files to Rojo project structure.

## Features

- **RBXL to RBXLX Conversion**: Uses Lune's native RBXL parser for reliable conversion
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
2. Click "Browse" to select your RBXL file
3. Choose an output directory
4. Click "Convert to Rojo Project"
5. Your Rojo project will be generated with all scripts, GUIs, and RemoteEvents!

## Limitations

- Requires Lune to be installed
- Only extracts from the target services (ServerScriptService, ReplicatedStorage, etc.)
- Some instance properties may not be preserved in the conversion



## License

MIT License - See LICENSE file for details.

You are free to use, modify, and distribute this software. Attribution is required if used in your projects.
