# Datasheets

Manufacturer datasheets for every active component. Links rather than local
copies, since manufacturers revise them and a stale PDF is worse than none.

| Part | Function | Datasheet |
|---|---|---|
| NE555 | Timer, astable clock source | [TI SNAS548](https://www.ti.com/lit/ds/symlink/ne555.pdf) |
| CD4017B | CMOS decade counter, 10 decoded outputs | [TI CD4017B](https://www.ti.com/lit/ds/symlink/cd4017b.pdf) |
| CD4075B | CMOS triple 3-input OR gate | [TI CD4075B](https://www.ti.com/lit/ds/symlink/cd4075b.pdf) |
| SN74LS47 | BCD to seven-segment decoder/driver | [TI SN5447A](https://www.ti.com/lit/ds/symlink/sn5447a.pdf) |

## The pages that matter

Rather than reading four full datasheets, these are the specific sections
this design depends on:

**NE555** — the astable configuration and its frequency equation. Everything
else (monostable, bistable, 50 % duty modifications) is out of scope here.

**CD4017** — the pin assignment table. Its decoded outputs are not in pin
order and this is where the most common build error comes from. Also the
Master Reset description: it is **asynchronous and active HIGH**, which is
what makes the `Q6 → MR` fold work.

**CD4075** — the pin assignment for the three gates. The logic is trivial;
only the pinout is worth looking up.

**74LS47** — the function table, which gives the segment pattern for every
BCD input, and the note that outputs are **active LOW with open collectors**.
That single fact determines the display type and mandates the series
resistors.

Extracts from these appear as figures in the original report — see
[`../images/figures/`](../images/figures/).

## Absolute maximum ratings

Worth reading once, because it settles the supply-voltage question:

| Part | Supply range | Absolute max |
|---|---|---|
| NE555 | 4.5 – 16 V | 18 V |
| CD4017 | 3 – 15 V | 18 V |
| CD4075 | 3 – 15 V | 18 V |
| **74LS47** | **4.75 – 5.25 V** | **7 V** |

The board runs at 5 V. Discussion in [`../BOM.md`](../BOM.md#supply-voltage).

## Local copies

If you add PDFs to this directory, name them `<part>-<manufacturer>.pdf`
(e.g. `cd4017b-ti.pdf`) and note the revision date, so it is obvious when a
copy has gone stale.
