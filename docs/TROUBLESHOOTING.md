# Troubleshooting

Ordered roughly by how often each fault actually occurs on this build, not by severity. Start at the top.

Before anything else, confirm three things with a meter:

1. The supply is **5 V**, not 12 V and not 3.3 V.
2. Every IC has **VCC and GND actually connected** — an unpowered chip behaves like a broken one.
3. The display is **common anode**.

---

## The display shows a `7`

**Cause:** CD4017 Master Reset is wired to pin 6 instead of pin 5.

`Q6` is on **pin 5**. Pin 6 is `Q7`. Feeding `Q7` back to MR makes a mod-7 counter, so the seventh state is stable and gets decoded — as `7`, since the OR network has no term for it and all three inputs happen to go HIGH.

**Fix:** move the MR wire to pin 5. Verify with `python3 tools/logic_verify.py`, which includes this exact case as a negative control.

This is the most common fault on the circuit by a wide margin, and the reason [ASSEMBLY.md](ASSEMBLY.md#cd4017-pinout) prints the pinout table twice.

---

## Every digit is inverted — dark where it should be lit

**Cause:** common-cathode display fitted instead of common anode.

The 74LS47 has **active-LOW** outputs. It lights a segment by pulling its cathode toward ground, which requires the anodes to be commoned at +5 V.

**Fix:** replace with a common-anode display. To confirm before buying: with the display out of circuit, put a meter in diode-test mode on the common pin. If the common pin is the *anode*, current flows from common to each segment pin. If it flows the other way, it is common cathode.

**Do not** try to fix this with a 74LS48 — that part has active-HIGH outputs and would work, but its internal pull-ups are weak and it drives a display poorly without external transistors.

---

## Nothing lights at all

Work down this list in order:

| Check | Expected |
|---|---|
| Supply voltage at the board | 5 V |
| VCC pin on each IC | 5 V |
| GND pin on each IC | 0 V |
| 74LS47 LT (pin 3) | +5 V — if grounded, actually shows `8`, so this is not it |
| 74LS47 BI/RBO (pin 4) | **+5 V** — if LOW, the decoder blanks completely |
| Display common pin | +5 V |
| Series resistors fitted | 220 Ω each, present on all seven lines |

**Most likely:** BI/RBO (pin 4) floating or grounded. That pin blanks the entire display when LOW and it is easy to leave unconnected — TTL inputs float HIGH, which usually saves you, but not reliably.

**Quick isolation:** ground LT (pin 3) momentarily. If `8` appears, the decoder, resistors and display are all fine and the fault is upstream in the counter or OR network. If nothing appears, the fault is in the display, the resistors, or the power to the 74LS47.

---

## Display is stuck on one digit

**Cause:** the clock is not running.

| Check | Expected |
|---|---|
| NE555 pin 4 (RESET) | +5 V — if LOW, the oscillator is held off |
| NE555 pin 2 tied to pin 6 | yes — required for astable mode |
| NE555 pin 3 (OUT) | should be switching; an LED and 1 kΩ will show it at these frequencies |
| Timing capacitor | fitted, and the electrolytic the correct way round |
| CD4017 pin 13 (CE) | GND — if HIGH, the counter is inhibited |

**If pin 3 is switching but the count does not advance:** the fault is between NE555 pin 3 and CD4017 pin 14, or CE (pin 13) is not grounded.

**If pin 3 is static:** the NE555 is not oscillating. Almost always pin 4 not at +5 V, or pin 2 and 6 not tied together.

---

## Counter skips digits intermittently

**Cause:** missing supply decoupling.

The NE555's output stage draws a sharp current spike on every transition. Without a local 100 nF capacitor, that spike shows up as a dip on the supply rail, and the CD4017 can register it as an extra clock edge.

**Fix:** 100 nF ceramic between VCC and GND at **every** IC, as physically close to the package as you can get it. Plus one 100 µF electrolytic where power enters the board.

This is the fault that most looks like a logic error and most is not. If your circuit works on a bench supply but misbehaves on a battery, or works when you touch the board and stops when you let go, this is it.

Secondary cause: switch bounce on a button wired into the clock path. See [ASSEMBLY.md](ASSEMBLY.md#debouncing).

---

## One digit in the sequence is wrong, the rest are correct

**Cause:** a single wire between the CD4017 and CD4075.

The counter and decoder are both fine — a fault in either would corrupt several digits, not one. Use the wrong digit to identify the wire:

| Shows | Should be | Diagnosis |
|:---:|:---:|---|
| 0 | 1 | `Q0` (pin 3) not reaching gate A |
| 1 | 3 | `Q2` (pin 4) not reaching gate B |
| 2 | 3 | `Q2` (pin 4) not reaching gate A |
| 0 | 2 | `Q1` (pin 2) not reaching gate B |
| 4 | 5 | `Q4` (pin 10) not reaching gate A |
| 5 | 4 | spurious HIGH into gate A |
| 4 | 6 | `Q5` (pin 1) not reaching gate B |
| 2 | 6 | `Q5` (pin 1) not reaching gate C |
| 3 | 1 | extra `Qn` wired into gate B |

The rule underneath: a **missing bit** means a `Qn` is not reaching its gate; an **extra bit** means a `Qn` is wired to a gate it does not belong to.

Cross-check against `python3 tools/logic_verify.py --table`, which prints the intended mapping.

---

## One segment never lights

**Cause:** in decreasing order of likelihood — open series resistor, broken wire, damaged display segment, damaged 74LS47 output.

**Isolation:** ground LT (pin 3) to force `8`. Every segment should light. If one stays dark under lamp test, the fault is in that segment's resistor, its wire, or the display itself — not in any of the logic.

To distinguish resistor from display: measure the resistor out of circuit, then briefly ground the display side of it and see whether the segment lights.

---

## One segment is always lit

**Cause:** a segment line shorted to ground, or a damaged 74LS47 output stuck LOW.

**Isolation:** tie 74LS47 pin 4 (BI/RBO) to ground. This forces every output HIGH and the display should go completely dark. If one segment stays lit, that line is shorted to ground somewhere between the decoder pin and the display — check for a solder bridge or a stray strand.

---

## Both displays show the same digit

**Cause:** the two channels are sharing a clock.

Each channel needs its own NE555. If both CD4017 clock pins trace back to the same oscillator, the counters advance in lockstep and always agree — one die shown twice.

**Fix:** confirm each channel has an independent NE555, then confirm the timing capacitors actually differ. With identical capacitors the channels drift only by component tolerance and will appear synchronised for long stretches.

---

## Digits are readable during the spin

**Not a fault — a design characteristic.**

At 9.43 Hz (10 µF), the fast channel flickers rather than blurs. At 0.94 Hz (100 µF), the slow channel is a readable count. Persistence of vision needs roughly **20 Hz** before digits genuinely smear.

**Fix:** reduce the timing capacitors.

| C | f | Perception |
|---|---|---|
| 1 µF | 94.3 Hz | blur |
| 2.2 µF | 42.9 Hz | blur |
| 4.7 µF | 20.1 Hz | marginal |
| 10 µF | 9.43 Hz | flicker |
| 100 µF | 0.94 Hz | readable count |

Recommended pair: **1 µF and 2.2 µF**. Reasoning in [THEORY.md](THEORY.md#choosing-the-spin-rate).

```bash
python3 tools/timing_calculator.py --sweep
```

---

## Frequency does not match the calculation

**Usually not a fault.** Electrolytic capacitors are commonly ±20 % and drift with temperature and age. A measured frequency 20 % off the calculated value is normal.

**If it is off by more than about 2×**, check:

- The capacitor value marking — 10 µF versus 100 µF is one digit and a very easy misread.
- Electrolytic polarity. A reverse-fitted electrolytic behaves erratically and will eventually fail, sometimes energetically.
- R₁ and R₂ actually measure what you think. Colour bands under poor light are unreliable; measure them.

---

## A chip gets hot

**Power down immediately.**

| Likely cause | Check |
|---|---|
| Supply is 12 V, not 5 V | Measure it. 12 V destroys the 74LS47. |
| Chip inserted backwards | Pin 1 orientation against the notch |
| Segment lines with no series resistors | All seven fitted? |
| Output shorted to ground or to another output | Look for solder bridges |
| Two gate outputs tied together | Never tie CMOS outputs — each drives its own node |

A 74LS47 that has seen 12 V is dead even if it appears to work; replace it rather than debugging around it.

---

## Nothing above matches

Bisect the signal path. Each stage can be tested independently of the ones before it:

| Test | Proves |
|---|---|
| Ground LT (pin 3) → shows `8` | Decoder, resistors, display all good |
| Drive A/B/C by hand → correct digits | BCD bus and decoder good |
| Manual clock → `Q0`…`Q5` walk | Counter and mod-6 fold good |
| Probe CD4075 outputs against the truth table | OR network good |
| LED on NE555 pin 3 → blinks | Clock good |

The first test that fails locates the stage. Full procedure in [ASSEMBLY.md](ASSEMBLY.md#build-order).

If the hardware checks out but the logic still seems wrong, run the verifier — it will tell you whether the *design* is at fault or only the build:

```bash
python3 tools/logic_verify.py --table
```
