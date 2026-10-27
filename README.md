# FIFA Street 2 — Native PC Port | No Emulated Xbox Hardware

> [!WARNING]
> This repository does **not** include the game, an ISO/XBE, EA assets, generated game code or a precompiled executable.
> You need your own original-Xbox USA disc. See [the full notice](#notice) at the end.

> [!TIP]
> **New: play without a controller.** The keyboard now plays as an Xbox controller, with the basic actions of **EA SPORTS FC 27's default WASD layout**: WASD to move, **L** pass, **;** shoot, **K** lob, **O** through ball, **P** sprint, **Esc** pause. See [Keyboard controls](#keyboard-controls).

An experimental port of the original-Xbox FIFA Street 2 built through static recompilation, with native PC graphics, audio and input. It is the sibling of the [FIFA Street (2005) port](https://github.com/batatinhafcbatatinha-pixel/fifa-street-pc) and reuses its runtime and native layers with this game's own addresses. **This public repository is a source and local-build kit, not a ready-to-play game download.** The game's x86 code is translated locally from your own verified disc; no game executable or generated game code is distributed here.

## Status

- Tested on Windows 11 x64: boot, menus, full matches at 60 fps, goal replays, game over, Rule The Street player creator, and saves (written and loaded back).
- Graphics: Direct3D 8 reimplemented in C on Direct3D 11 (or Vulkan through DXVK). Resolutions up to 4K and ultrawide were tested at 60 fps. Aspect options: the game's own 16:9 widescreen (with bars on wider screens) or **21:9 hor+**, which extends the scenery to the screen edges.
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

The xboxrecomp toolkit is the `xboxrecomp/` submodule ([batatinhafcbatatinha-pixel/xboxrecomp](https://github.com/batatinhafcbatatinha-pixel/xboxrecomp), branch `ports`): clone with `git clone --recursive`, or run `git submodule update --init` in an existing clone. The source-kit ZIP from Releases includes it; GitHub's **Code → Download ZIP** does not.

```powershell
python -m pip install -r requirements.txt
python tools/build_local.py --game-files game_files --llvm-dir "C:\Program Files\LLVM"
python tools/play.py --game-files game_files
```

`build_local.py`:

1. validates your files;
2. takes the xboxrecomp runtime and translator from the `xboxrecomp/` submodule;
3. disassembles your `default.xbe` with this game's function seeds and translates it into private C under `.local/`;
4. applies the post-passes (interrupt acknowledgement, frame-pointer boundaries, serialized heap code, native API wrappers) and compiles the port.

The first build takes a while. `--reuse-generated` skips the translation on later builds.

## Keyboard controls

No controller needed: the keyboard plays as an Xbox controller, with the keys of the default **WASD** layout of EA SPORTS FC 27 ([EA's layout chart](https://help.ea.com/en/articles/ea-sports-fc/mouse-keyboard/)) on the buttons FIFA used on the original Xbox. Only the basic actions are mapped for now.

| Key | In a match | In menus | Controller button |
| --- | --- | --- | --- |
| **W A S D** | Move the player | Navigate | Left stick |
| **Arrows** | | Navigate | D-pad |
| **L** | Pass | Confirm | A |
| **;** (**Ç** on ABNT2 keyboards) | Shoot | Back | B |
| **K** | Lob pass / cross | | X |
| **O** | Through pass | | Y |
| **P** | Sprint | | Right trigger |
| **Enter** | | Confirm, passes *PRESS START* | A + Start |
| **Esc** | Pause | | Start |
| **Backspace** | | Back | B |
| **Tab** | | | Back |

The keyboard drives player 1 and is merged with a controller plugged in there, so both work at the same time. Tricks (right stick), the white/black buttons and the left trigger are not mapped on the keyboard yet. The launcher turns the keyboard on (`RECOMP_KEYBOARD=1`); set `RECOMP_KEYBOARD=0` to turn it off.

## Controls and settings

Xbox controllers work as on the console. **F1** or **Back + Start** opens the PC settings (display mode, resolution, aspect, VSync, frame limit, graphics API, FXAA, MSAA (off, 2x/4x/8x or the 2x the Xbox game asks for), anisotropic filtering, language, volume). **Alt + Enter** toggles fullscreen.

The PC settings screen is drawn in the game's own style (graffiti title, paper poster, black selection stroke, tan value bands with white arrows) with the game's fonts, FifaStreet_Title Leigh and EAS SansCondensed. They are read from your disc (`data/aptanims/aptfnts.big`) when the game starts and are not part of this repository. On the main menu and the Options screens a **BACK · PC Settings** hint shows that the controller's Back button opens it there. The menu is in English by default; *Menu language* switches it to Portuguese.

## Credits and licenses

- Port integration and native backend work: [batatinhafcbatatinha-pixel](https://github.com/batatinhafcbatatinha-pixel).
- [xboxrecomp](https://github.com/sp00nznet/xboxrecomp): **Ned Heller / sp00nz** and contributors (MIT). The modified copy used here is the fork [batatinhafcbatatinha-pixel/xboxrecomp](https://github.com/batatinhafcbatatinha-pixel/xboxrecomp) (branch `ports`), with all its notices and licenses, included as the `xboxrecomp/` submodule; see `street2/project/LICENSE.xboxrecomp`. `tools/translate-ebp-boundaries.py` comes from [fifa-street-pc](https://github.com/batatinhafcbatatinha-pixel/fifa-street-pc).
- [xemu](https://github.com/xemu-project/xemu) contributors for LGPL/GPL runtime components credited in that snapshot's notices (present in the runtime, not started by this port's profile).
- [DXVK](https://github.com/doitsujin/dxvk) (zlib), [vkd3d-shader](https://gitlab.winehq.org/wine/vkd3d) (LGPL) and DejaVu fonts: optional external dependencies; licenses in `licenses/`.
- [Capstone](https://www.capstone-engine.org/): disassembler used by the translator (installed through `requirements.txt`).
- FIFA Street 2, its game code, trademarks and assets belong to Electronic Arts and the respective rights holders. This project is not affiliated with or endorsed by EA or Microsoft.

See [NOTICE.md](NOTICE.md) for the publication boundary and [LICENSE](LICENSE) for the license of the port's own code.

---

<a id="notice"></a>

**⚠️ THIS PROJECT DOES NOT INCLUDE THE GAME, AN ISO/XBE, EA GAME ASSETS, GENERATED GAME CODE OR A PRECOMPILED GAME EXECUTABLE. YOU MUST PROVIDE YOUR OWN LAWFULLY OBTAINED ORIGINAL-XBOX USA GAME FILES AND HAVE THE RIGHTS REQUIRED FOR YOUR USE. THIS PROJECT DOES NOT AUTHORIZE COPYRIGHT INFRINGEMENT. ALL GAME RIGHTS BELONG TO THEIR RESPECTIVE OWNERS. ⚠️**
