Source kit only: no game, no XBE, no generated code and no executable. Bring your own original-Xbox USA disc.

- Native Direct3D 8 on Direct3D 11/Vulkan, native DirectSound and XInput; no NV2A, APU/DSP, AC97 or USB model started.
- `tools/extract_iso.py` + `tools/validate_game.py`: extract your disc and verify the supported revision by SHA-256.
- `tools/build_local.py`: downloads the pinned xboxrecomp runtime, translates your XBE locally and builds the port.
- Tested on Windows 11 x64: menus, full matches at 60 fps, replays, player creator and saves.
