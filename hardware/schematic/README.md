# Schematic

## Files

| File | Contents |
|---|---|
| `digital-dice-schematic.pdf` | Schematic export, "Digital Dice Fix", 20/12/2024 |

The PDF is the authoritative drawing. A pin-by-pin transcription that is
easier to follow while wiring is in
[`../netlist/digital-dice.net`](../netlist/digital-dice.net).

## Reference designators

| Designator | Part | Channel |
|---|---|:---:|
| U3 | NE555 | 1 |
| U2 | CD4017 | 1 |
| U5, U6, U9 | CD4075 (OR_3) | 1 |
| U1 | 74LS47 | 1 |
| U4 | CD4017 | 2 |
| U8, U11, U12 | CD4075 (OR_3) | 2 |
| U7 | 74LS47 | 2 |
| R1 | 5.1 kΩ | timing |
| R2, R3 | 1 kΩ | MR pull-down |
| C1 | 100 µF | timing, slow channel |
| C2 | 10 µF | timing, fast channel |

## Known gaps in the export

The export does not annotate every passive per channel. Specifically:

1. Only one 5.1 kΩ resistor (R1) is labelled, though the standard astable
   needs two per NE555. The netlist reference assumes R1 = R2 = 5.1 kΩ.
2. Only one NE555 (U3) appears in the extracted text, although the bill of
   materials specifies two and two independent clocks are required for the
   design to work as described.
3. Segment series resistors are not shown. They are mandatory — see
   [`../../docs/ASSEMBLY.md`](../../docs/ASSEMBLY.md#segment-current-limiting).

**Measure your own board before quoting any of these values.** The
consequences of each assumption are flagged in the netlist file.

## Contributing a source file

The repository ships a PDF, which cannot be edited. A KiCad, EasyEDA or
Proteus source file would let others modify the design. If you redraw it,
please open a pull request — see [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md).
