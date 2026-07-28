# Datasheets

Manufacturer datasheets for every active component. Links rather than local
copies, since manufacturers revise them and a stale PDF is worse than none.

| Part | Function | Datasheet |
|---|---|---|
| NE555 | Timer, astable clock source | [TI SNAS548](https://www.ti.com/lit/ds/symlink/ne555.pdf) |
| CD4017B | CMOS decade counter, 10 decoded outputs | [TI CD4017B](https://www.ti.com/lit/ds/symlink/cd4017b.pdf) |
| CD4075B | CMOS triple 3-input OR gate | [TI CD4075B](https://www.ti.com/lit/ds/symlink/cd4075b.pdf) |
| SN74LS47 | BCD to seven-segment decoder/driver | [TI SN5447A](https://www.ti.com/lit/ds/symlink/sn5447a.pdf) |

## Absolute maximum ratings

Worth reading once, because it settles the supply-voltage question:

| Part | Supply range | Absolute max |
|---|---|---|
| NE555 | 4.5 – 16 V | 18 V |
| CD4017 | 3 – 15 V | 18 V |
| CD4075 | 3 – 15 V | 18 V |
| **74LS47** | **4.75 – 5.25 V** | **7 V** |
