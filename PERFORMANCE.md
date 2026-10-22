# Renderer update — 2026-10-22

The native renderer avoids rebinding unchanged D3D11 state and uploading
identical constant buffers. Changed textures with matching dimensions, mip
count and format receive new texels in place. Uncompressed conversion selects
the format outside the pixel loop; YUV video converts pairs with shared chroma
arithmetic. Rendering resolution, pixel calculations and timing defaults are
preserved.

## Validation

Windows / RTX 3050 Laptop GPU / D3D11, 1920×1080 internal resolution, VSync and
frame limit off, monitor index 1 (75 Hz). Two 160-second runs alternated caches
and texture reuse every 600 frames within the same match. Intro/loading were
excluded. Selected gameplay windows had at least 250 draws/frame and less
than 0.1 ms average build work; consecutive on/off pairs differed by at most
15% in their draw counts.

| Measurement | First run, off → on | Repeat, off → on |
|---|---:|---:|
| Selected pairs | 10 | 13 |
| Mean frame time | 6.489 → 6.167 ms | 6.558 → 6.103 ms |
| Throughput | 154.11 → 162.15 fps | 152.49 → 163.85 fps |
| Draw cost per call | 4.335 → 3.773 µs | 4.297 → 3.755 µs |
| Draw cost reduction | 12.96% | 12.61% |
| Worst frame | 23.1 → 40.0 ms | 18.0 → 19.0 ms |
| Frames over 20 ms | 1 → 6 | 0 → 0 |

The first run's six optimized-mode pauses clustered in one window. Its worst
frame spent 1.75 ms in measured draw work, 0.17 ms presenting and zero time
building resources; the remaining delay is outside those measured renderer
phases. The 40-ms pause did not recur in the repeat. Its cause has not been
established, and these results do not prove that all frame-time spikes are
fixed. Average throughput improved about 5–7% in the measured gameplay windows.

Both production converters matched the pre-update native converter exactly
in 798 synthetic cases each, including odd YUV widths, missing palettes,
padded rows and output guards. A separate capped run's 19 captures covered
menus, gameplay, goals, replay and Gamebreaker. Both updated Windows builds
and runtime comparisons completed without unresolved native calls. Six kit
tool tests and the publication audit passed. A fresh private generation from
the public kit was not repeated; the four changed kit source files match the
tested development files. These observations cover one machine and one match
configuration. Uncapped mode accelerates the simulation; normal-play defaults
remain unchanged.

## Diagnostics

- `RECOMP_HLE_PROFILE=1`: timings and CPU use every 600 frames.
- `RECOMP_HLE_AB=1` with profiling: alternate optimization modes each window.
- `RECOMP_HLE_NO_STATE_CACHE=1`: rebind state every draw.
- `RECOMP_HLE_NO_CB_SKIP=1`: upload constants even when unchanged.
- `RECOMP_HLE_NO_TEX_REUSE=1`: recreate changed textures.
- `RECOMP_HLE_MONITOR=1`: select the second monitor for tests.
- `RECOMP_HLE_FPS=0` and `RECOMP_HLE_VSYNC=0`: uncapped throughput testing.

Per-draw clock queries run only while profiling. No new effect toggles were
added. Glow, depth-of-field and motion-blur properties were found in script
objects; their values are copied or animated into rendering objects. An
independently verified control is still needed before exposing these in F1.
