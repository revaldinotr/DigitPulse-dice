# Assembly and Bring-Up

Build order, complete pin maps, and a test procedure that isolates faults to a single stage.

- [Before you start](#before-you-start)
- [Build order](#build-order)
- [Pin maps](#pin-maps)
- [Stage 1 — power and display](#stage-1--power-and-display)
- [Stage 2 — decoder](#stage-2--decoder)
- [Stage 3 — counter](#stage-3--counter)
- [Stage 4 — OR network](#stage-4--or-network)
- [Stage 5 — clock](#stage-5--clock)
- [Stage 6 — second channel](#stage-6--second-channel)
- [Segment current limiting](#segment-current-limiting)
- [Decoupling](#decoupling)
- [Buttons](#buttons)

---

## Before you start

> [!WARNING]
> **Run this board at 5 V.** The 74LS47 is TTL with an absolute maximum supply of 7 V. The 12 V listed in the original proposal will destroy it immediately. The CMOS parts tolerate 3–15 V, but a mixed board runs at the lowest ceiling on it. See [BOM.md](BOM.md#supply-voltage).

> [!IMPORTANT]
> **The display must be common ANODE.** The 74LS47 has active-LOW outputs and sinks current. A common-cathode display will show the photographic negative of every digit.

Three habits that save the most time on this build:

- **Bring up one channel completely before starting the second.** When channel 2 misbehaves you will want a known-good channel to compare against, probe by probe.
- **Power down before rewiring.** CMOS inputs are static-sensitive and hot-plugging a logic input into a driven output is a good way to lose a chip.
- **Check the CD4017 pin order against the table below every single time.** Its decoded outputs are not in numerical order and this is the most common fault on this circuit by a wide margin.

Tools: a multimeter is sufficient for everything here. An oscilloscope makes stage 5 faster but is not required — an LED on the NE555 output tells you what you need to know at these frequencies.

---

## Build order

Build **backwards**, from the display toward the clock. Each stage is then verified using only the stages already built, so a fault can only be in the part you just added.

```
  Stage 5        Stage 4       Stage 3      Stage 2      Stage 1
  NE555   --->   CD4075  --->  CD4017  ---> 74LS47  ---> display
  clock          OR net        counter      decoder      + power

  <---------------- build direction -----------------
```

| Stage | Add | Verified by |
|:---:|---|---|
| 1 | Power rail, display, series resistors | Grounding a segment line by hand |
| 2 | 74LS47 | Lamp test (LT low → shows `8`) |
| 3 | CD4017 | Manual clock pulses, watch the count |
| 4 | CD4075 | Digits 1–6 in sequence on manual clock |
| 5 | NE555 | Automatic spin |
| 6 | Second channel | Both displays, out of phase |

---

## Pin maps

### CD4017 pinout

The decoded outputs are **not** in pin order. Copy this table onto paper and check against it while wiring.

| Signal | Pin | Goes to |
|---|:---:|---|
| `Q0` | **3** | CD4075 gate A input 1 |
| `Q1` | **2** | CD4075 gate B input 1 |
| `Q2` | **4** | CD4075 gate A input 2, gate B input 2 |
| `Q3` | **7** | CD4075 gate C input 1 |
| `Q4` | **10** | CD4075 gate A input 3, gate C input 2 |
| `Q5` | **1** | CD4075 gate B input 3, gate C input 3 |
| `Q6` | **5** | **MR (pin 15)** — the mod-6 fold |
| `Q7` | 6 | no connect |
| `Q8` | 9 | no connect |
| `Q9` | 11 | no connect |
| CO | 12 | no connect |
| CLK | 14 | NE555 pin 3 |
| CE | 13 | GND |
| MR | 15 | `Q6` (pin 5), plus 1 kΩ to GND |
| VDD | 16 | +5 V |
| VSS | 8 | GND |

Note especially: `Q5` is on **pin 1** and `Q6` on **pin 5**. Wiring pin 6 to MR yields a mod-7 counter that displays a phantom `7`.

### 74LS47 pinout

| Signal | Pin | Goes to |
|---|:---:|---|
| A (weight 1) | **7** | CD4075 gate A output |
| B (weight 2) | **1** | CD4075 gate B output |
| C (weight 4) | **2** | CD4075 gate C output |
| D (weight 8) | **6** | **GND** |
| LT | 3 | +5 V |
| BI/RBO | 4 | +5 V |
| RBI | 5 | +5 V |
| Qa | 13 | display `a`, via 220 Ω |
| Qb | 12 | display `b`, via 220 Ω |
| Qc | 11 | display `c`, via 220 Ω |
| Qd | 10 | display `d`, via 220 Ω |
| Qe | 9 | display `e`, via 220 Ω |
| Qf | 15 | display `f`, via 220 Ω |
| Qg | 14 | display `g`, via 220 Ω |
| VCC | 16 | +5 V |
| GND | 8 | GND |

The BCD input pins are also out of order: A is pin 7, B is pin 1, C is pin 2, D is pin 6.

### CD4075 pinout

Three independent 3-input OR gates.

| Gate | Inputs | Output | Used for |
|:---:|---|:---:|---|
| 1 | 3, 4, 5 | 6 | `A = Q0 + Q2 + Q4` |
| 2 | 1, 2, 8 | 9 | `B = Q1 + Q2 + Q5` |
| 3 | 11, 12, 13 | 10 | `C = Q3 + Q4 + Q5` |

VDD is pin 14, VSS is pin 7. Gate assignment is arbitrary — any gate can serve any output — but keep it consistent between the two channels so debugging transfers.

### NE555 astable

| Pin | Name | Connect to |
|:---:|---|---|
| 1 | GND | ground |
| 2 | TRIG | junction of R₂ and C (tie to pin 6) |
| 3 | OUT | CD4017 pin 14 |
| 4 | RESET | +5 V |
| 5 | CTRL | 100 nF to ground |
| 6 | THRESH | tie to pin 2 |
| 7 | DISCH | junction of R₁ and R₂ |
| 8 | VCC | +5 V |

R₁ from +5 V to pin 7. R₂ from pin 7 to pin 6. C from pin 6 to ground.

---

## Stage 1 — power and display

Wire the +5 V and ground rails. Fit the display and its seven 220 Ω series resistors, with the common pin to **+5 V**.

**Test:** with the resistors in place but the 74LS47 not yet fitted, briefly touch the free end of each series resistor to ground. Each should light exactly one segment. Work through all seven and note the mapping — display pinouts vary by part number and this five-minute check is worth far more than assuming.

If a segment is dim or dead: wrong resistor value, a cracked display, or the common pin on ground instead of +5 V.

---

## Stage 2 — decoder

Fit the 74LS47. Connect VCC, GND, all seven segment outputs, and tie LT, BI/RBO and RBI to +5 V. Ground input D (pin 6). Leave A, B, C unconnected for now — **or better, tie them to ground temporarily**, since floating TTL inputs read as HIGH and will show a `0`.

**Test A — lamp test.** Momentarily connect pin 3 (LT) to ground. All seven segments should light, showing `8`.

This single action verifies the decoder, all seven outputs, all seven resistors, and the display, independent of any input logic. If `8` appears cleanly, everything downstream of the BCD bus is proven correct and you never need to suspect it again.

**Test B — manual BCD.** Return LT to +5 V. Drive A, B, C by hand between ground and +5 V and confirm the digits:

| C | B | A | Expect |
|:-:|:-:|:-:|:-:|
| 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 1 |
| 0 | 1 | 0 | 2 |
| 0 | 1 | 1 | 3 |
| 1 | 0 | 0 | 4 |
| 1 | 0 | 1 | 5 |
| 1 | 1 | 0 | 6 |
| 1 | 1 | 1 | 7 |

The last row is the useful one: driving all three HIGH gives `7`, which confirms the decoder can produce it and therefore that the *circuit's* inability to show `7` comes from the counter and the grounded D input — not from a broken decoder. Worth seeing once.

> [!TIP]
> If the pattern is inverted — segments off where they should be on — you have a common-cathode display. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Stage 3 — counter

Fit the CD4017. Connect VDD (16), VSS (8), CE (13) to ground, and MR (15) to `Q6` (**pin 5**) with a 1 kΩ resistor from MR to ground.

Do **not** connect the NE555 yet. Instead run pin 14 (CLK) through a 10 kΩ resistor to ground, and clock it manually by briefly touching pin 14 to +5 V.

**Test:** wire an LED with a 1 kΩ resistor to each of `Q0`…`Q5` in turn, or probe with a meter. Manual clocks should walk through `Q0` → `Q1` → `Q2` → `Q3` → `Q4` → `Q5` → `Q0`.

You will never see `Q6` HIGH — that is correct, it self-erases in nanoseconds. If the sequence includes a seventh state, MR is on the wrong pin.

> [!NOTE]
> Manual clocking through a bare wire will bounce and may skip several states per touch. That is contact bounce, not a fault. What matters is that the sequence never reaches a seventh state.

---

## Stage 4 — OR network

Fit the CD4075. Wire the three gates per the [pin map](#cd4075-pinout), then connect the gate outputs to the 74LS47 inputs A, B, C. Leave D grounded.

**Test:** clock manually again. The display should now read **1, 2, 3, 4, 5, 6, 1, 2, …**

If a digit is wrong, the fault is one wire between the CD4017 and CD4075. Compare the wrong digit against the expected BCD to find it:

| Shows | Should show | Missing / extra |
|:---:|:---:|---|
| 0 | 1 | `Q0` not reaching gate A |
| 2 | 3 | `Q2` not reaching gate A |
| 1 | 3 | `Q2` not reaching gate B |
| 5 | 4 | spurious HIGH on gate A |
| 4 | 5 | `Q4` not reaching gate A |
| 7 | 6 | spurious HIGH on gate A — check `Q4`/`Q0`/`Q2` wiring |

The pattern to internalise: a **missing** digit-bit means a `Qn` is not reaching its gate; an **extra** bit means a `Qn` is wired to a gate it does not belong to.

---

## Stage 5 — clock

Remove the manual clock wire. Build the NE555 astable per the [pin map](#ne555-astable) and connect pin 3 to CD4017 pin 14.

Start with **C = 10 µF** to match the original build, or **1 µF** for the recommended faster spin ([THEORY.md](THEORY.md#choosing-the-spin-rate)).

**Test:** the display should cycle 1–6 continuously. At 10 µF it flickers visibly at about 9 Hz; at 1 µF it blurs.

Verify the frequency before trusting it:

```bash
python3 tools/timing_calculator.py --r1 5.1k --r2 5.1k --c 10u
```

If the display sits on one digit, the NE555 is not oscillating — check pin 4 (RESET) is at +5 V, and that pin 2 is tied to pin 6.

---

## Stage 6 — second channel

Repeat stages 1–5 with a different timing capacitor. Everything else is identical.

| Channel | C as built | C recommended |
|---|---|---|
| 1 | 10 µF | 1 µF |
| 2 | 100 µF | 2.2 µF |

**Test:** both displays cycle, visibly out of step. Watch for thirty seconds — they should never lock into phase. If they do, the two channels are sharing a clock somewhere.

---

## Segment current limiting

Every segment line needs a series resistor. This is not optional.

The 74LS47 has open-collector outputs rated to sink 24 mA at 0.4 V. A red LED segment drops about 2 V. Without a series resistor:

$$I = \frac{5\ \mathrm{V} - 2\ \mathrm{V} - 0.4\ \mathrm{V}}{R_{\text{wiring}}} \approx \text{limited only by wire resistance}$$

which will exceed the output rating and destroy the driver, the segment, or both.

With 220 Ω:

$$I = \frac{5 - 2 - 0.4}{220} = \frac{2.6}{220} \approx 12\ \mathrm{mA}$$

Comfortably inside the 24 mA rating, and bright.

| R | Current | Result |
|---|---|---|
| 150 Ω | 17 mA | brighter, still within rating |
| 220 Ω | 12 mA | **recommended** |
| 330 Ω | 8 mA | dimmer, fine indoors |
| 1 kΩ | 2.6 mA | too dim to read in daylight |

> [!CAUTION]
> A single resistor on the display's common pin instead of seven individual resistors is a common shortcut and it does not work. Brightness would then depend on how many segments are lit — `1` (two segments) would glare while `8` (seven segments) would be dim. Worse, the total current through that one resistor scales with segment count. One resistor per segment.

---

## Decoupling

Fit a **100 nF ceramic capacitor between VCC and GND at every IC**, physically as close to the package as possible.

This is skipped more often than any other step and it causes the most confusing faults. The NE555's output stage draws a sharp current spike on every transition; without local decoupling that spike appears as a supply dip which the CD4017 can read as a spurious clock edge. The symptom is a counter that skips digits intermittently — a fault that looks like bad logic and is actually a power problem.

Also fit **one 100 µF electrolytic across the supply rails** at the point where power enters the board.

The 100 nF on NE555 pin 5 (CTRL) is separate and additional — it stabilises the internal reference divider.

---

## Buttons

The original design uses three buttons: spin, stop, reset.

| Button | Wire to | Effect |
|---|---|---|
| Spin / stop | NE555 pin 4 (RESET) to GND | Halts the oscillator; the counter freezes on the current digit |
| Reset | CD4017 pin 15 (MR) to +5 V | Forces the display back to `1` |

Holding NE555 RESET low is the cleanest way to stop, because it freezes the clock without disturbing the counter state — the displayed digit is exactly the one that was current.

### Debouncing

None of the buttons is debounced in the original build. A bouncy press on the reset line can inject several MR pulses, which is harmless. A bouncy press on a clock line would inject extra counts, which is not.

Two straightforward fixes:

- **100 nF across the switch contacts.** Cheap, adequate for a reset line.
- **74HC14 Schmitt-trigger inverter with an RC input.** Clean and reliable, worth it if the button ever drives a clock.

This is listed as a known limitation in the [README](../README.md#known-limitations) rather than silently fixed, because the as-built circuit is what the report documents.

---

## Bring-up checklist

- [ ] Supply is **5 V**, verified with a meter, not assumed
- [ ] Display is **common anode**
- [ ] 100 nF decoupling at every IC
- [ ] 100 µF bulk capacitor at the supply entry
- [ ] CD4017 MR wired to **pin 5**, not pin 6
- [ ] 1 kΩ from MR to ground
- [ ] CD4017 CE (pin 13) grounded
- [ ] 74LS47 D input (pin 6) grounded
- [ ] 74LS47 LT, BI/RBO, RBI all at +5 V
- [ ] Seven 220 Ω resistors, one per segment
- [ ] NE555 RESET (pin 4) at +5 V
- [ ] NE555 pin 2 tied to pin 6
- [ ] Lamp test shows a clean `8`
- [ ] Manual clock walks 1–6 with no seventh state
- [ ] Both channels run out of phase

If something is wrong at any point, [TROUBLESHOOTING.md](TROUBLESHOOTING.md) is ordered by how often each fault actually occurs.
