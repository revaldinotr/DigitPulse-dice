# Enclosure

The 3D enclosure design from the original project. The render is in
[`../../docs/images/figures/18-desain-3d.png`](../../docs/images/figures/18-desain-3d.png).

## Status

Source CAD files are not in this repository. If you have the original STL,
STEP or Fusion 360 files, adding them here would make the project genuinely
reproducible — the electronics are fully documented, the mechanics are not.

## Requirements for a replacement design

Anyone modelling a new enclosure needs to accommodate:

| Element | Constraint |
|---|---|
| Two seven-segment displays | Cutouts sized to the display body, typically 0.56" |
| Three push buttons | Spin, stop, reset — reachable one-handed |
| Board | Perfboard or breadboard footprint, whichever you built on |
| Power entry | 5 V, USB or barrel jack |
| Ventilation | Minimal — total draw is well under 500 mA |

The buttons matter more than they look. This is a dice: it gets pressed
repeatedly, quickly, and often by someone not looking at it. Recessed or
stiff buttons make the device unpleasant in a way that is invisible in a
render.

## Contributing

STL and source CAD both welcome. Please include the units and the printer
settings you used — see [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md).
