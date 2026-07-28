# Theory of Operation

How a decade counter, three OR gates and a BCD decoder become a pair of dice — and why each of those choices was made rather than an easier one.

- [The problem, stated precisely](#the-problem-stated-precisely)
- [Folding a decade counter into mod-6](#folding-a-decade-counter-into-mod-6)
- [Deriving the OR network](#deriving-the-or-network)
- [Why the gate count is not a coincidence](#why-the-gate-count-is-not-a-coincidence)
- [The 74LS47 and active-LOW outputs](#the-74ls47-and-active-low-outputs)
- [Choosing the spin rate](#choosing-the-spin-rate)
- [Why not the CD4026](#why-not-the-cd4026)
- [Randomness: an honest assessment](#randomness-an-honest-assessment)
- [Complete truth tables](#complete-truth-tables)

---

## The problem, stated precisely

Build a device that displays a value uniformly drawn from {1, 2, 3, 4, 5, 6} on a seven-segment display, using only discrete logic, and do it twice with the two results independent.

Three components suggest themselves immediately, and none of them fits:

| Part | What it does | Why it doesn't fit alone |
|---|---|---|
| NE555 | Produces a clock | Has no notion of a number |
| CD4017 | Counts 0–9, one-hot output | Ten states, not six; one-hot, not BCD |
| 74LS47 | Drives a seven-segment display | Needs 4-bit BCD, not one-hot |

The design is the glue between them. Two gaps must be closed:

1. **Ten states → six states.** A range problem.
2. **One-hot → BCD.** An encoding problem.

They are independent, and each has a clean solution.

---

## Folding a decade counter into mod-6

The CD4017 has a Master Reset (MR, pin 15) that is **asynchronous and active HIGH**. Asserting it forces the counter to `Q0` immediately, without waiting for a clock edge.

That gives a one-wire solution: **connect `Q6` (pin 5) to MR (pin 15)**.

Trace what happens on the clock edge that would produce the seventh state:

```
edge 6 arrives
  -> counter advances to state 6
  -> Q6 goes HIGH
  -> MR sees HIGH
  -> counter resets to Q0            (asynchronous — no clock needed)
  -> Q6 goes LOW
  -> MR releases
```

The entire excursion through state 6 lasts one propagation delay through the counter's reset path — on the order of tens of nanoseconds at 5 V. The display, driven through a decoder and LEDs with millisecond-scale response, never resolves it. The observable sequence is:

```
Q0 → Q1 → Q2 → Q3 → Q4 → Q5 → Q0 → ...
```

Six stable states. Exactly a d6.

> [!IMPORTANT]
> `Q6` is on **pin 5**, not pin 6. The CD4017's decoded outputs are deliberately scrambled across the package to simplify its internal layout. The full mapping is in [ASSEMBLY.md](ASSEMBLY.md#cd4017-pinout). Wiring pin 6 to MR gives a mod-7 counter that shows a phantom `7`, which is the single most common failure on this build.

### Why MR needs a pull-down

`Q6` is HIGH for nanoseconds per cycle and LOW otherwise, so MR is driven the vast majority of the time. But CMOS inputs must never be left in an indeterminate state during power-up transients, when the counter's outputs have not yet settled. A **1 kΩ resistor from MR to ground** holds it defined without meaningfully loading `Q6` when it does assert. This is the `R2`/`R3` in the netlist.

### The alternative that was rejected

The other way to get six states is to gate the clock — count to six, then inhibit further edges via Clock Enable (pin 13). This requires a latch to remember that six has been reached, plus a reset path to clear it, and it stops the counter rather than wrapping it. For a dice that must cycle continuously while spinning, wrapping is what is wanted. The `Q6 → MR` fold costs one wire and one resistor.

---

## Deriving the OR network

The CD4017 asserts exactly one output at a time — a **one-hot** code. The 74LS47 expects a **weighted binary** code on inputs A (1), B (2), C (4), D (8). Converting between them is a fixed combinational problem.

Assign `Q0` → digit 1, `Q1` → digit 2, … `Q5` → digit 6. Write the binary expansion of each target digit:

| Counter state | Digit | D (8) | C (4) | B (2) | A (1) |
|---|:---:|:---:|:---:|:---:|:---:|
| `Q0` | 1 | 0 | 0 | 0 | **1** |
| `Q1` | 2 | 0 | 0 | **1** | 0 |
| `Q2` | 3 | 0 | 0 | **1** | **1** |
| `Q3` | 4 | 0 | **1** | 0 | 0 |
| `Q4` | 5 | 0 | **1** | 0 | **1** |
| `Q5` | 6 | 0 | **1** | **1** | 0 |

A one-hot input has a useful property: since exactly one `Qn` is HIGH at any moment, **a BCD output bit is HIGH precisely when the active `Qn` is one of the states where that bit should be set**. So each output bit is simply the OR of the states in whose row it carries a 1.

Read the table by column:

- Column **A** has 1s in the rows for `Q0`, `Q2`, `Q4` → `A = Q0 + Q2 + Q4`
- Column **B** has 1s in the rows for `Q1`, `Q2`, `Q5` → `B = Q1 + Q2 + Q5`
- Column **C** has 1s in the rows for `Q3`, `Q4`, `Q5` → `C = Q3 + Q4 + Q5`
- Column **D** is all zeros → `D = GND`

No Karnaugh map, no minimisation. One-hot encoding makes the sum-of-products form already minimal: each product term is a single literal, so there is nothing to factor.

---

## Why the gate count is not a coincidence

Three OR gates, three inputs each. The CD4075 is a **triple 3-input OR gate**. One package, nothing left over.

That fit is worth a second look, because it comes from an underlying symmetry rather than luck.

Each BCD bit position *b* is HIGH for exactly half of any complete run of $2^n$ consecutive integers. Over the six digits 1–6:

| Bit | Digits where it is set | Count |
|---|---|:---:|
| A (1) | 1, 3, 5 | 3 |
| B (2) | 2, 3, 6 | 3 |
| C (4) | 4, 5, 6 | 3 |
| D (8) | — | 0 |

The three low bits each land on exactly three of the six digits. Six is $2 \times 3$, and the low three bit-positions partition the range evenly — so a 3-input gate is exactly the right width, three times over.

Had the design targeted a d8 (digits 1–8), bit A would be set for {1,3,5,7} and the gates would need four inputs. Had it targeted a d4, two-input gates would suffice. The d6 case is the one that fits a CD4075 exactly, which is a small piece of luck sitting on top of a real structural fact.

### The consequence that matters

`D` is tied to ground. Not left floating, not driven LOW by a gate — physically connected to the 0 V rail.

The 74LS47 decodes 8 and 9 only when `D` is HIGH. With `D` grounded, **digits 8 and 9 have no electrical path to the display**. And because `Q6` self-erases, neither 0 nor 7 is ever presented to the decoder.

The specification "shows only 1 to 6" is therefore a property of the board's topology, not a behaviour that has to be maintained. There is no line of reasoning that, if got wrong, produces a `7`. This is what discrete logic buys you over four lines of firmware, and it is the reason the project is worth building this way.

---

## The 74LS47 and active-LOW outputs

The 74LS47 converts 4-bit BCD to seven segment lines. Its outputs are **active LOW**: an output pin driven LOW lights its segment.

This dictates the display type. A **common-anode** display ties all segment anodes to +5 V; each segment lights when its cathode is pulled toward ground — which is exactly what a LOW output does.

> [!WARNING]
> Fitting a **common-cathode** display produces an inverted pattern: every segment that should be lit is dark and vice versa. A `1` appears as the five segments that are *not* `b` and `c`. This does not damage anything, but it is baffling if the polarity is not the first thing you check.

### The three control inputs

| Pin | Name | Active | Function | Wire to |
|:---:|---|:---:|---|---|
| 3 | LT | LOW | Lamp test — forces all segments on, displaying `8` | +5 V |
| 4 | BI/RBO | LOW | Blanking input — forces all segments off | +5 V |
| 5 | RBI | LOW | Ripple blanking — suppresses a leading zero | +5 V |

All three are held HIGH (inactive) in normal operation. They are useful during bring-up: momentarily grounding **LT** displays `8`, which confirms every segment, every series resistor and the display itself in one action, independent of whether the counter or OR network is working. [ASSEMBLY.md](ASSEMBLY.md) uses this as the first test.

### Segment patterns

| BCD | Digit | Segments lit | Outputs LOW |
|:---:|:---:|---|---|
| 0001 | 1 | b, c | 12, 11 |
| 0010 | 2 | a, b, d, e, g | 13, 12, 10, 9, 14 |
| 0011 | 3 | a, b, c, d, g | 13, 12, 11, 10, 14 |
| 0100 | 4 | b, c, f, g | 12, 11, 15, 14 |
| 0101 | 5 | a, c, d, f, g | 13, 11, 10, 15, 14 |
| 0110 | 6 | c, d, e, f, g | 11, 10, 9, 15, 14 |

Note that `6` here does **not** light segment `a`. That is the 74LS47 datasheet pattern, and it renders as a `6` without a top bar. Some decoders include `a`. Neither is wrong; it is a font difference, and worth knowing before assuming the chip is faulty.

---

## Choosing the spin rate

The NE555 astable period is

$$t_{high} = 0.693(R_1 + R_2)C \qquad t_{low} = 0.693 R_2 C$$

$$f = \frac{1.44}{(R_1 + 2R_2)C} \qquad \text{duty} = \frac{R_1 + R_2}{R_1 + 2R_2}$$

Duty cycle in this topology is always above 50 %, because the capacitor charges through $R_1 + R_2$ but discharges through $R_2$ alone. **This does not matter here.** The CD4017 advances on rising edges only, so each digit is displayed for exactly one full period regardless of the high/low split.

### What the frequency actually controls

The clock frequency determines whether a human perceives a *spin* or a *count*:

| Frequency | Perception | Suitable for |
|---|---|---|
| > 20 Hz | Digits blur into an unreadable smear | A convincing spin |
| 4–20 Hz | Visible flicker, digits partly trackable | Neither, really |
| < 4 Hz | A readable count | A deliberate countdown |

The threshold near 20 Hz is persistence of vision — above it the eye integrates successive digits rather than resolving them.

### As built

| Channel | R₁ | R₂ | C | f | Digit dwell | Full cycle | Perception |
|---|---|---|---|---|---|---|---|
| 1 (fast) | 5.1 kΩ | 5.1 kΩ | 10 µF | 9.43 Hz | 106 ms | 636 ms | fast flicker |
| 2 (slow) | 5.1 kΩ | 5.1 kΩ | 100 µF | 0.94 Hz | 1.06 s | 6.36 s | visible count |

The 10× ratio between channels is the design's headline feature and it works: two independent clocks means the displays never lock in phase, so stopping them gives two genuinely separate results.

### The honest critique

Both channels sit on the wrong side of the perception thresholds.

At **9.43 Hz** the fast channel flickers rather than blurs. A player can follow the digits and, with practice, time the button press.

At **0.94 Hz** the slow channel is not a spin at all — it is a one-second-per-digit count. A player can simply wait for the digit they want and press. This is a **fairness defect**, not an aesthetic one: the outcome stops being random and starts being a reaction-time skill test.

### The fix

Move both channels above 20 Hz while keeping them mutually incommensurate. Keeping R₁ = R₂ = 5.1 kΩ:

| C | f | Perception |
|---|---|---|
| 1 µF | 94.3 Hz | blur |
| 2.2 µF | 42.9 Hz | blur |
| 4.7 µF | 20.1 Hz | blur, marginal |
| 10 µF | 9.43 Hz | flicker ← as built |
| 100 µF | 0.94 Hz | count ← as built |

**Recommended revision: 1 µF and 2.2 µF.** Both blur convincingly, the ratio is 2.2× rather than 10× — still enough that the channels drift apart, and both are fast enough that no human reaction time can select a face.

Explore other combinations with:

```bash
python3 tools/timing_calculator.py --sweep
python3 tools/timing_calculator.py --target-hz 40 --c 1u
```

> [!NOTE]
> Electrolytic capacitors are commonly ±20 % and drift with temperature and age. Measured frequencies of ±20 % against the table are normal and not a fault. For this application the imprecision is harmless — arguably beneficial, since it adds variation between units.

---

## Why not the CD4026

The initial proposal ([`docs/Proposal-Awal-OhmFusion.pdf`](Proposal-Awal-OhmFusion.pdf)) specified the **CD4026B**, which combines a decade counter and a seven-segment driver in one package. That is a simpler parts list: NE555 + CD4026 + display, versus NE555 + CD4017 + CD4075 + 74LS47 + display.

The final build changed to the split architecture. The reasoning:

**The CD4026 gives you nowhere to intervene.** Its counter and decoder are internally bonded — the BCD bus never appears on a pin. Restricting the output to 1–6 means manipulating the counter's reset alone, which gets you six *consecutive* states but always starting at 0: the sequence 0–5, not 1–6. Producing 1–6 requires either relabelling the display, adding an offset stage anyway, or accepting a die that can roll a zero.

**The split architecture exposes the BCD bus,** and that is where the constraint belongs. Tying `D` to ground makes 8 and 9 unreachable by inspection of the board. On a CD4026 there is no equivalent — the restriction lives inside the package where it cannot be seen or measured.

**For a Digital Electronics course, the exposed version is the assignable one.** The CD4026 build demonstrates that you can read a datasheet. The CD4017 + CD4075 + 74LS47 build demonstrates one-hot to binary conversion, asynchronous reset feedback, active-LOW driver polarity, and combinational minimisation — the actual syllabus.

The trade is two extra ICs per channel for a design where every requirement is visible on the schematic. For teaching, and for a portfolio, that is the right side of the trade. For a product, the CD4026 would win on cost.

---

## Randomness: an honest assessment

**This device is not a random number generator.** It is a deterministic counter sampled at a user-chosen instant.

Entropy comes from one place: the phase of the free-running clock at the moment the button is pressed, relative to human reaction time. Two conditions must hold for the result to be fair:

1. **The clock must be fast relative to the precision of human timing.** Human press timing has a standard deviation of roughly 20–50 ms. At 94 Hz (10.6 ms per digit) that spread covers several digits, so the outcome is uncontrollable. At 0.94 Hz (1.06 s per digit) it covers 2–5 % of one digit, and the player has effectively full control.

2. **The player must not be able to see and track the sequence.** Above the persistence-of-vision threshold this is automatic.

Both conditions fail on the slow channel as built, and the fast channel is marginal. The revision recommended above satisfies both.

Even after the fix, the distribution is uniform only insofar as press timing is uncorrelated with clock phase. A player deliberately pressing at a fixed interval after the previous result could introduce bias. For a board game this is well past the point of caring; the honest statement is that this is a **fair-enough dice, not a source of entropy**, and nothing here should be used where randomness has consequences.

A genuinely unbiased hardware approach would sample avalanche noise from a reverse-biased transistor junction, or use ring-oscillator jitter. Both are considerably more involved and out of scope for this project — but they are the right answer to "how would you make this actually random", which is a question worth being ready for.

---

## Complete truth tables

### CD4017 with `Q6 → MR`

| Clock edge | State | HIGH output | Pin | Digit shown |
|:---:|:---:|:---:|:---:|:---:|
| 0 | 0 | `Q0` | 3 | 1 |
| 1 | 1 | `Q1` | 2 | 2 |
| 2 | 2 | `Q2` | 4 | 3 |
| 3 | 3 | `Q3` | 7 | 4 |
| 4 | 4 | `Q4` | 10 | 5 |
| 5 | 5 | `Q5` | 1 | 6 |
| 6 | *6* | *`Q6` → MR* | *5* | *never resolves* |
| 6 | 0 | `Q0` | 3 | 1 |

### One-hot → BCD → segments

| `Qn` | A | B | C | D | BCD | Digit | Segments |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `Q0` | 1 | 0 | 0 | 0 | 0001 | 1 | b c |
| `Q1` | 0 | 1 | 0 | 0 | 0010 | 2 | a b d e g |
| `Q2` | 1 | 1 | 0 | 0 | 0011 | 3 | a b c d g |
| `Q3` | 0 | 0 | 1 | 0 | 0100 | 4 | b c f g |
| `Q4` | 1 | 0 | 1 | 0 | 0101 | 5 | a c d f g |
| `Q5` | 0 | 1 | 1 | 0 | 0110 | 6 | c d e f g |

### CD4075 3-input OR

| A | B | C | Q |
|:-:|:-:|:-:|:-:|
| 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 1 |
| 0 | 1 | 0 | 1 |
| 0 | 1 | 1 | 1 |
| 1 | 0 | 0 | 1 |
| 1 | 0 | 1 | 1 |
| 1 | 1 | 0 | 1 |
| 1 | 1 | 1 | 1 |

Since the CD4017 output is one-hot, only the rows with a single 1 are ever exercised in this circuit. The remaining rows are unreachable — which is itself a useful invariant: if you ever measure two OR inputs HIGH simultaneously, the counter has failed, not the gate.

---

All tables above are generated and checked by [`tools/logic_verify.py`](../tools/logic_verify.py). If you change the mapping, run it — it will tell you whether the design still holds.

```bash
python3 tools/logic_verify.py --table
```
