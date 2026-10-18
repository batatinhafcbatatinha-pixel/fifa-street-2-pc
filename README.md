# FIFA Street 2 — Native PC Port | No Emulated Xbox Hardware

> [!WARNING]
> This repository does **not** include the game, an ISO/XBE, EA assets, generated game code or a precompiled executable.
> You need your own original-Xbox USA disc. See [the full notice](#notice) at the end.

An experimental port of the original-Xbox FIFA Street 2 built through static recompilation, with native PC graphics, audio and input. It is the sibling of the [FIFA Street (2005) port](https://github.com/batatinhafcbatatinha-pixel/fifa-street-pc) and reuses its runtime and native layers with this game's own addresses. **This public repository is a source and local-build kit, not a ready-to-play game download.** The game's x86 code is translated locally from your own verified disc; no game executable or generated game code is distributed here.

## Status

- Tested on Windows 11 x64: boot, menus, full matches at 60 fps, goal replays, game over, Rule The Street player creator, and saves (written and loaded back).
- Graphics: Direct3D 8 reimplemented in C on Direct3D 11 (or Vulkan through DXVK). Resolutions up to 4K and ultrawide were tested at 60 fps.
- Audio: DirectSound reimplemented in C with its own mixer, output through XAudio2.
- Input: XInput reimplemented on host pads and the keyboard.
- No NV2A GPU, APU/DSP, AC97 or USB model is started. The Xbox kernel and memory layout remain as compatibility layers.
- Windows x64 only for now.

## Why a native port instead of an emulator

An emulator such as [xemu](https://github.com/xemu-project/xemu) recreates the original Xbox: it translates the console's CPU code at run time and models the NV2A GPU, the audio DSP and the USB controllers register by register. That is the right approach for the whole library. This port takes a different route for one game:

- **Ahead-of-time code.** The game's x86 code is translated into C and compiled by a modern optimizing compiler.
- **No emulated hardware in the hot path.** Direct3D 8, DirectSound and XInput calls go straight to C implementations on Direct3D 11, XAudio2 and host pads, instead of being lowered to push-buffer commands, DSP microcode and USB packets that are emulated again.
- **Resolution and widescreen beyond the console**, rendered by the PC GPU at any internal resolution.
- **Readable and fixable.** Each hook and native layer is plain C in `street2/project/src`.

The trade-off: it covers only this game and revision, and it is experimental. An emulator is the more general and better-tested option.

## Your game files

Only the **original Xbox USA** revision is accepted. Extract your own disc image into a folder named `game_files` and validate it:

```sh
python tools/extract_iso.py "FIFA Street 2 (USA).iso" --output game_files
python tools/validate_game.py game_files
```

```text
default.xbe  5fabb5b763be0cc8823e814ee343ac5be6950305330f46c5170e08eaadea910b
```

Do not upload the ISO, extracted files, generated code or the built executable.

## Build on Windows

Requirements: Python 3.10+ (with `pip install -r requirements.txt`), Visual Studio 2022 Build Tools (C++ workload, Windows SDK), LLVM/Clang (`clang-cl`), CMake and Ninja.

```powershell
python -m pip install -r requirements.txt
python tools/build_local.py --game-files game_files --llvm-dir "C:\Program Files\LLVM"
python tools/play.py --game-files game_files
```

`build_local.py`:

1. validates your files;
2. downloads the xboxrecomp runtime and translator from a pinned commit of the public [fifa-street-pc](https://github.com/batatinhafcbatatinha-pixel/fifa-street-pc) repository (the same runtime this port was tested with);
3. disassembles your `default.xbe` with this game's function seeds and translates it into private C under `.local/`;
4. applies the post-passes (interrupt acknowledgement, frame-pointer boundaries, serialized heap code, native API wrappers) and compiles the port.

The first build takes a while. `--reuse-generated` skips the translation on later builds.

## Controls and settings

Xbox controllers work as on the console. **F1** or **Back + Start** opens the PC settings (display mode, resolution, aspect, VSync, frame limit, graphics API, FXAA, anisotropic filtering, language, volume). **Alt + Enter** toggles fullscreen.

| Keyboard | Action |
| --- | --- |
| Arrows | D-pad |
| Numpad 8 / 4 / 2 / 6 | Left stick |
| I / J / K / L | Right stick |
| Z / X / A / S | A / B / X / Y |
| Q / E | White / Black |
| 1 / 3 | Left / Right trigger |
| Enter or Esc | Start |
| Backspace | Back |

## Credits and licenses

- Port integration and native backend work: [batatinhafcbatatinha-pixel](https://github.com/batatinhafcbatatinha-pixel).
- [xboxrecomp](https://github.com/sp00nznet/xboxrecomp): **Ned Heller / sp00nz** and contributors (MIT). The modified runtime snapshot is published, with all its notices and licenses, in [fifa-street-pc](https://github.com/batatinhafcbatatinha-pixel/fifa-street-pc) and downloaded at build time; see `street2/project/LICENSE.xboxrecomp`.
- [xemu](https://github.com/xemu-project/xemu) contributors for LGPL/GPL runtime components credited in that snapshot's notices (present in the runtime, not started by this port's profile).
- [DXVK](https://github.com/doitsujin/dxvk) (zlib), [vkd3d-shader](https://gitlab.winehq.org/wine/vkd3d) (LGPL) and DejaVu fonts: optional external dependencies; licenses in `licenses/`.
- [Capstone](https://www.capstone-engine.org/): disassembler used by the translator (installed through `requirements.txt`).
- FIFA Street 2, its game code, trademarks and assets belong to Electronic Arts and the respective rights holders. This project is not affiliated with or endorsed by EA or Microsoft.

See [NOTICE.md](NOTICE.md) for the publication boundary and [LICENSE](LICENSE) for the license of the port's own code.

---

<a id="notice"></a>

**⚠️ THIS PROJECT DOES NOT INCLUDE THE GAME, AN ISO/XBE, EA GAME ASSETS, GENERATED GAME CODE OR A PRECOMPILED GAME EXECUTABLE. YOU MUST PROVIDE YOUR OWN LAWFULLY OBTAINED ORIGINAL-XBOX USA GAME FILES AND HAVE THE RIGHTS REQUIRED FOR YOUR USE. THIS PROJECT DOES NOT AUTHORIZE COPYRIGHT INFRINGEMENT. ALL GAME RIGHTS BELONG TO THEIR RESPECTIVE OWNERS. ⚠️**
