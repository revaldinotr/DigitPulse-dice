# Simulation

Simulate the circuit before committing to solder. Each tool below substitutes
different parts, and each diverges from the physical board in a way worth
knowing about before you trust the result.

## Which tool

| Tool | Cost | Best for | Main limitation |
|---|---|---|---|
| **Proteus** | paid | Closest to the real build — has NE555, CD4017, 74LS47 and animated seven-segment displays | Licence cost; slow at high clock rates |
| **Falstad Circuit Simulator** | free, browser | Understanding the logic quickly, no install | No CD4017 or 74LS47 — must be built from primitives |
| **Logisim Evolution** | free | The combinational part in isolation | Digital only — cannot simulate the NE555 at all |
| **LTspice** | free | The NE555 timing network | Poor at digital logic; use it for the oscillator only |

A reasonable division of labour: **LTspice for the clock, Logisim for the
logic, Proteus for the whole thing.**

## Proteus

Parts are available under these names:

| Circuit part | Proteus library name |
|---|---|
| NE555 | `555` |
| CD4017 | `4017` |
| CD4075 | `OR_3` (three per package) or `4075` |
| 74LS47 | `74LS47` |
| Display | `7SEG-COM-ANODE` |

The schematic export in
[`../hardware/schematic/digital-dice-schematic.pdf`](../hardware/schematic/digital-dice-schematic.pdf)
was produced from Proteus, so the reference designators in
[`../hardware/netlist/digital-dice.net`](../hardware/netlist/digital-dice.net)
match its component names directly.

**Where it diverges from the real board:**

- Proteus ignores supply decoupling. The intermittent digit-skipping caused
  by missing 100 nF capacitors — the most confusing real-world fault on this
  circuit — will never appear in simulation.
- Its seven-segment model does not need series resistors. The real one does,
  and omitting them destroys hardware.
- Switch bounce is not modelled unless you add it deliberately.

## Falstad

Runs in a browser at <https://falstad.com/circuit/>. It has no CD4017 or
74LS47, so build the logic from primitives:

- **CD4017** → a 4-bit counter feeding a 4-to-16 decoder, using only the
  first six outputs
- **CD4075** → three 3-input OR gates from the logic menu
- **74LS47** → Falstad has a `7-Segment Decoder` under *Outputs and Labels*,
  but its outputs are active HIGH. Either invert them or use its
  common-cathode display.

Good for confirming the OR mapping in a couple of minutes. Not useful for
timing.

## Logisim Evolution

Digital only, so the NE555 has to be replaced by Logisim's clock component.
That is fine — the point of a Logisim model is the combinational part.

Build:

1. Clock → counter (set to 6 states, or use a 10-state counter with a
   comparator driving reset)
2. Decoder → six one-hot lines
3. Three OR gates per the mapping in
   [`../docs/THEORY.md`](../docs/THEORY.md#deriving-the-or-network)
4. Logisim's built-in seven-segment display

Logisim will let you single-step the clock, which makes the mod-6 fold easy
to watch. Note that Logisim's reset is synchronous by default while the
CD4017's is asynchronous — so in Logisim the seventh state may be visible for
one tick where on real hardware it is not.

## LTspice

Use it for the NE555 astable alone. Most NE555 SPICE models are third-party;
the one bundled with LTspice under `Misc` works.

Sweep the timing capacitor to see the frequency change, then cross-check
against:

```bash
python3 ../tools/timing_calculator.py --sweep
```

The calculator uses the ideal formula. SPICE will show a small discrepancy
from the NE555's internal comparator offsets — typically under 5 %, which is
far smaller than the ±20 % tolerance of the electrolytic capacitor you will
actually fit.

## What no simulator will tell you

- Whether the display is common anode or common cathode — that is a purchase
  decision, and it is the second most common failure on this build
- Whether decoupling is adequate
- Whether the CD4017 Master Reset is on pin 5 or pin 6 — the pinout is where
  the most common failure lives, and simulation hides pin numbers behind
  symbolic connections

For those, see [`../docs/ASSEMBLY.md`](../docs/ASSEMBLY.md).
