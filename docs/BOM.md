# Bill of Materials

Parts for one complete two-display unit, plus substitutions, sourcing notes, and the supply-voltage correction.

- [Supply voltage](#supply-voltage)
- [Full parts list](#full-parts-list)
- [Integrated circuits](#integrated-circuits)
- [Passives](#passives)
- [Display](#display)
- [Substitutions](#substitutions)
- [Estimated cost](#estimated-cost)

---

## Supply voltage

> [!WARNING]
> **This board runs at 5 V.** The original proposal ([`Proposal-Awal-OhmFusion.pdf`](Proposal-Awal-OhmFusion.pdf)) specifies a 12 V supply. Do not use it.

The reasoning is worth stating fully because the error is easy to make and destructive.

| Part | Family | Supply range | Absolute max |
|---|---|---|---|
| NE555 | Bipolar | 4.5 – 16 V | 18 V |
| CD4017 | CMOS | 3 – 15 V | 18 V |
| CD4075 | CMOS | 3 – 15 V | 18 V |
| **74LS47** | **TTL** | **4.75 – 5.25 V** | **7 V** |

Three of the four parts are comfortable at 12 V. The 74LS47 is not — it is a 74LS-series TTL device with an absolute maximum supply of 7 V, and 12 V will destroy it, typically within seconds.

**A mixed-family board runs at the lowest ceiling on it.** With a 74LS47 present, that ceiling is 5 V, and 5 V sits inside every other part's range. So the correct rail is 5 V for the whole board — there is no reason to run the CMOS parts higher and every reason not to.

If you keep the 12 V supply for another reason (motor, backlight, higher-voltage display), regulate down to 5 V with a **7805** before any logic. A 7805 dropping 12 V to 5 V at 200 mA dissipates 1.4 W and needs a heatsink.

> [!NOTE]
> A 74HC4511 could replace the 74LS47 and would tolerate a higher rail — but it drives common-**cathode** displays with active-HIGH outputs, so it is not a drop-in. See [Substitutions](#substitutions).

---

## Full parts list

For the complete two-channel unit.

| # | Component | Value / part | Qty | Notes |
|:---:|---|---|:---:|---|
| 1 | Timer IC | NE555 / LM555 | 2 | One per channel — do **not** share |
| 2 | Decade counter | CD4017BE | 2 | Also sold as HEF4017, MC14017 |
| 3 | Triple 3-input OR | CD4075BE | 2 | Exactly three gates needed per channel |
| 4 | BCD → 7-seg decoder | 74LS47 | 2 | TTL, active LOW, **5 V only** |
| 5 | 7-segment display | 1 digit, **common anode** | 2 | Anode type is mandatory |
| 6 | Resistor | 5.1 kΩ, ¼ W | 4 | NE555 timing, 2 per channel |
| 7 | Resistor | 1 kΩ, ¼ W | 2 | CD4017 MR pull-down |
| 8 | Resistor | 220 Ω, ¼ W | 14 | Segment limiting, 7 per display |
| 9 | Capacitor | 10 µF electrolytic | 1 | Timing, fast channel |
| 10 | Capacitor | 100 µF electrolytic | 1 | Timing, slow channel |
| 11 | Capacitor | 100 nF ceramic | 10 | Decoupling — 8 for ICs, 2 for NE555 pin 5 |
| 12 | Capacitor | 100 µF electrolytic | 1 | Bulk supply decoupling |
| 13 | Push button | tactile, momentary | 3 | Spin / stop / reset |
| 14 | Supply | 5 V regulated, ≥ 300 mA | 1 | USB supply is ideal |
| 15 | IC socket | DIP-8 | 2 | Optional but strongly recommended |
| 16 | IC socket | DIP-16 | 6 | Optional but strongly recommended |
| 17 | Breadboard or perfboard | — | 1 | — |
| 18 | Jumper wire | — | as needed | — |

> [!TIP]
> **Use IC sockets.** Eight ICs is enough that one wrong insertion is likely, and desoldering a 16-pin DIP without damaging perfboard is unpleasant. Sockets also let you swap a suspect chip in seconds during bring-up.

### If you take the recommended timing revision

Replace items 9 and 10 with **1 µF and 2.2 µF**, which move both channels above the persistence-of-vision threshold. See [THEORY.md](THEORY.md#choosing-the-spin-rate).

---

## Integrated circuits

### NE555

Bipolar timer, running as a free-running astable. One per channel — sharing a single timer between channels defeats the entire "different spin times" premise.

The CMOS variants (**TLC555**, **LMC555**) draw far less current and are pin-compatible. If you run from a battery, they are a straightforward upgrade. Their output drive is lower, which is irrelevant here since the load is one CMOS clock input.

### CD4017

CMOS decade counter with ten decoded one-hot outputs. Advances on the **rising** clock edge.

Its decoded outputs are not in pin order — see [ASSEMBLY.md](ASSEMBLY.md#cd4017-pinout). Equivalent parts sold under HEF4017, MC14017, TC4017; all are pin-compatible.

### CD4075

Triple 3-input OR gate. All three gates are used, exactly filling the package.

**The 74HC4075 is not a substitute for the CD4075 without checking the supply.** Both are 3-input triple OR gates and pin-compatible, but the 74HC part is 2–6 V only. At 5 V either works.

### 74LS47

BCD to seven-segment decoder with **open-collector, active-LOW** outputs, designed to sink current from a common-anode display.

Two things to keep straight:

- **Active LOW** — a segment lights when its output is pulled LOW. This is what makes the common-anode display mandatory.
- **Open collector** — the outputs sink but do not source. Series resistors are required (see [ASSEMBLY.md](ASSEMBLY.md#segment-current-limiting)).

The **74LS48** is the active-HIGH counterpart for common-cathode displays, but its internal pull-ups are weak and it drives a display poorly without external transistors. Prefer the 47 with a common-anode display.

---

## Passives

### Timing resistors — 5.1 kΩ

Two per NE555. Standard ¼ W carbon film is fine; the timing tolerance of an electrolytic capacitor swamps any resistor tolerance you are likely to encounter.

Using different values changes both frequency and duty cycle:

```bash
python3 tools/timing_calculator.py --r1 10k --r2 5.1k --c 1u
```

### MR pull-down — 1 kΩ

Holds CD4017 Master Reset defined during power-up. Anything from 1 kΩ to 100 kΩ works. Lower values load `Q6` slightly more when it asserts; higher values are more susceptible to noise. 1 kΩ is a safe middle.

### Segment resistors — 220 Ω

Seven per display. Do **not** substitute a single resistor on the common pin — brightness would then vary with the number of lit segments. Full reasoning in [ASSEMBLY.md](ASSEMBLY.md#segment-current-limiting).

| Value | Current | Brightness |
|---|---|---|
| 150 Ω | 17 mA | bright, within the 24 mA rating |
| **220 Ω** | **12 mA** | **recommended** |
| 330 Ω | 8 mA | adequate indoors |
| 470 Ω | 5.5 mA | dim |

### Timing capacitors

Electrolytic, ±20 % typical. That tolerance is fine here — precision is not required and the resulting variation between units is arguably a feature.

**Watch the polarity.** A reverse-fitted electrolytic behaves erratically and will eventually fail, occasionally with force.

### Decoupling — 100 nF ceramic

One per IC, placed physically at the package. Plus one on NE555 pin 5 (CTRL).

These are the cheapest parts on the list and skipping them causes the most confusing fault on the board — intermittent digit skipping that looks exactly like a logic error. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md#counter-skips-digits-intermittently).

---

## Display

**Single-digit, common anode, 7 segments plus decimal point.** The decimal point is unused.

Common sizes: 0.36" (small, breadboard-friendly), 0.56" (good visibility, the usual choice), 1.0"+ (needs more current than the 74LS47 can sink directly — you would need transistor drivers).

### Verifying the type before you buy

Datasheet part numbers are inconsistent across suppliers. Test with a multimeter in diode mode:

- Probe the common pin and a segment pin. Note which polarity lights the segment faintly.
- **Common anode:** current flows from common → segment.
- **Common cathode:** current flows from segment → common.

Two-digit displays exist and would suit this project physically, but they multiplex the segment lines and need a scanning driver. That is a different circuit. Use two separate single-digit displays.

---

## Substitutions

| Original | Alternative | Drop-in? | Notes |
|---|---|:---:|---|
| NE555 | TLC555, LMC555 | yes | CMOS, much lower supply current |
| NE555 | 556 (dual) | no | One 556 replaces both 555s but changes the pinout entirely |
| CD4017 | HEF4017, MC14017, TC4017 | yes | Same part, different manufacturer |
| CD4075 | 74HC4075 | yes at 5 V | Narrower supply range (2–6 V) |
| CD4075 | 74LS32 (quad 2-input OR) | no | Needs 2 gates per 3-input OR → 6 gates, 2 packages |
| 74LS47 | 74LS247 | yes | Different font for `6` and `9` |
| 74LS47 | 74HC4511 | **no** | Active HIGH, common **cathode**, has a latch |
| 74LS47 | CD4511 | **no** | As above |
| Common anode display | Common cathode | **no** | Requires changing the decoder too |

> [!IMPORTANT]
> The 4511 family is the most tempting wrong substitution: it is a BCD-to-seven-segment decoder, it is CMOS, and it tolerates 12 V. But it drives **common cathode** displays with active-HIGH outputs and includes an input latch. Swapping it in requires changing the display type and rethinking the blanking inputs. It is a valid redesign, not a substitution.

---

## Estimated cost

Indicative retail prices for hobbyist quantities in Indonesia, late 2024. Bulk and marketplace prices are considerably lower.

| Item | Qty | Unit | Subtotal |
|---|:---:|---|---|
| NE555 | 2 | Rp 2.000 | Rp 4.000 |
| CD4017 | 2 | Rp 4.000 | Rp 8.000 |
| CD4075 | 2 | Rp 4.000 | Rp 8.000 |
| 74LS47 | 2 | Rp 6.000 | Rp 12.000 |
| 7-segment, common anode | 2 | Rp 3.000 | Rp 6.000 |
| Resistors, assorted | 20 | Rp 200 | Rp 4.000 |
| Capacitors, assorted | 12 | Rp 500 | Rp 6.000 |
| Push buttons | 3 | Rp 1.500 | Rp 4.500 |
| IC sockets | 8 | Rp 1.000 | Rp 8.000 |
| Breadboard / perfboard | 1 | Rp 15.000 | Rp 15.000 |
| Jumper wire | — | — | Rp 10.000 |
| **Total** | | | **≈ Rp 85.500** |

Excludes the 5 V supply (a spare phone charger works) and the enclosure.

For context: a microcontroller version costs less in parts — one ATtiny85 and one display — and demonstrates none of the digital logic the course is about. The extra Rp 40.000 buys a design where every requirement is visible on the schematic.

---

## Datasheets

Links and local copies in [`docs/datasheets/`](datasheets/).

| Part | Manufacturer datasheet |
|---|---|
| NE555 | [Texas Instruments SNAS548](https://www.ti.com/lit/ds/symlink/ne555.pdf) |
| CD4017 | [Texas Instruments CD4017B](https://www.ti.com/lit/ds/symlink/cd4017b.pdf) |
| CD4075 | [Texas Instruments CD4075B](https://www.ti.com/lit/ds/symlink/cd4075b.pdf) |
| 74LS47 | [Texas Instruments SN74LS47](https://www.ti.com/lit/ds/symlink/sn5447a.pdf) |
