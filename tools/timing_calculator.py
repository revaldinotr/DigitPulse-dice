#!/usr/bin/env python3
"""
timing_calculator.py — NE555 astable design aid for the digital dice.

The two dice channels are deliberately clocked at different rates so the
displays do not settle in lockstep. This script converts between component
values and the behaviour you actually see on the bench:

    * clock frequency and duty cycle of the NE555 astable
    * how long one full 1..6 cycle of the CD4017 takes
    * whether the digit reads as a blur (a "spin") or a visible count

Usage:
    python3 tools/timing_calculator.py                  # the two shipped channels
    python3 tools/timing_calculator.py --r1 5.1k --r2 5.1k --c 10u
    python3 tools/timing_calculator.py --target-hz 30 --c 10u   # solve for R
    python3 tools/timing_calculator.py --sweep           # capacitor options table

Formulae (NE555 astable, standard configuration):

    t_high = 0.693 * (R1 + R2) * C        capacitor charges through R1 + R2
    t_low  = 0.693 *  R2       * C        capacitor discharges through R2 only
    f      = 1.44 / ((R1 + 2*R2) * C)
    duty   = (R1 + R2) / (R1 + 2*R2)      always > 50 % in this topology

The CD4017 advances on the RISING edge, so one displayed digit lasts exactly
one clock period regardless of duty cycle. Duty cycle only affects the 555
output waveform, not the dwell time per digit.
"""

from __future__ import annotations

import argparse

LN2 = 0.6931471805599453

# Persistence of vision: above roughly 20 digit-changes per second the eye
# integrates the digits into an unreadable blur, which is what makes the
# device feel like a spinning dice rather than a counter.
BLUR_THRESHOLD_HZ = 20.0
COUNT_THRESHOLD_HZ = 4.0

E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

SI = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3,
      "k": 1e3, "K": 1e3, "M": 1e6}


def parse_value(text: str) -> float:
    """Accept '5.1k', '10u', '100n', '4700' and return a plain float."""
    text = text.strip().rstrip("ΩFf")
    if text and text[-1] in SI:
        return float(text[:-1]) * SI[text[-1]]
    return float(text)


def fmt_r(r: float) -> str:
    if r >= 1e6:
        return f"{r / 1e6:g} MΩ"
    if r >= 1e3:
        return f"{r / 1e3:g} kΩ"
    return f"{r:g} Ω"


def fmt_c(c: float) -> str:
    if c >= 1e-6:
        return f"{c * 1e6:g} µF"
    if c >= 1e-9:
        return f"{c * 1e9:g} nF"
    return f"{c * 1e12:g} pF"


def fmt_t(t: float) -> str:
    if t >= 1:
        return f"{t:.3f} s"
    if t >= 1e-3:
        return f"{t * 1e3:.2f} ms"
    return f"{t * 1e6:.1f} µs"


class Astable:
    def __init__(self, r1: float, r2: float, c: float):
        self.r1, self.r2, self.c = r1, r2, c

    @property
    def t_high(self) -> float:
        return LN2 * (self.r1 + self.r2) * self.c

    @property
    def t_low(self) -> float:
        return LN2 * self.r2 * self.c

    @property
    def period(self) -> float:
        return self.t_high + self.t_low

    @property
    def frequency(self) -> float:
        return 1.0 / self.period

    @property
    def duty(self) -> float:
        return (self.r1 + self.r2) / (self.r1 + 2 * self.r2)

    @property
    def cycle_time(self) -> float:
        """Time for the CD4017 to walk the full 1..6 sequence once."""
        return 6 * self.period

    def behaviour(self) -> str:
        f = self.frequency
        if f >= BLUR_THRESHOLD_HZ:
            return "blur — digits unreadable, reads as a true spin"
        if f >= COUNT_THRESHOLD_HZ:
            return "fast flicker — individual digits partly discernible"
        return "visible count — user can follow and time the button press"

    def report(self, label: str = "") -> str:
        head = f"NE555 astable{' — ' + label if label else ''}"
        lines = [
            head,
            "-" * max(46, len(head)),
            f"  R1              {fmt_r(self.r1)}",
            f"  R2              {fmt_r(self.r2)}",
            f"  C               {fmt_c(self.c)}",
            "",
            f"  t_high          {fmt_t(self.t_high)}",
            f"  t_low           {fmt_t(self.t_low)}",
            f"  period          {fmt_t(self.period)}",
            f"  frequency       {self.frequency:.2f} Hz",
            f"  duty cycle      {self.duty * 100:.1f} %",
            "",
            f"  one digit lasts {fmt_t(self.period)}",
            f"  full 1..6 cycle {fmt_t(self.cycle_time)}",
            f"  perceived as    {self.behaviour()}",
        ]
        return "\n".join(lines)


def solve_r2(target_hz: float, c: float, r1: float) -> float:
    """Given f, C and R1, find the R2 that hits the target frequency."""
    total = 1.44 / (target_hz * c)   # total = R1 + 2*R2
    r2 = (total - r1) / 2
    if r2 <= 0:
        raise ValueError(
            f"R1 = {fmt_r(r1)} is already too large for {target_hz} Hz at {fmt_c(c)}. "
            f"Reduce R1 below {fmt_r(total)} or pick a larger capacitor."
        )
    return r2


def nearest_e12(value: float) -> float:
    decade = 10 ** (len(f"{int(value)}") - 1) if value >= 1 else 1
    best, err = value, float("inf")
    for mult in (decade / 10, decade, decade * 10):
        for base in E12:
            cand = base * mult
            if abs(cand - value) < err:
                best, err = cand, abs(cand - value)
    return best


def sweep(r1: float, r2: float) -> str:
    caps = [1e-9, 10e-9, 100e-9, 1e-6, 2.2e-6, 4.7e-6, 10e-6, 22e-6, 47e-6, 100e-6, 220e-6]
    out = [
        f"Capacitor sweep at R1 = {fmt_r(r1)}, R2 = {fmt_r(r2)}",
        "-" * 62,
        f"  {'C':>8}  {'freq':>10}  {'period':>10}  {'1..6 cycle':>11}  behaviour",
        "  " + "-" * 58,
    ]
    for c in caps:
        a = Astable(r1, r2, c)
        tag = a.behaviour().split(" —")[0]
        out.append(
            f"  {fmt_c(c):>8}  {a.frequency:>8.2f} Hz  {fmt_t(a.period):>10}"
            f"  {fmt_t(a.cycle_time):>11}  {tag}"
        )
    out.append("")
    out.append(f"  A spin needs f > {BLUR_THRESHOLD_HZ:g} Hz; a readable count needs "
               f"f < {COUNT_THRESHOLD_HZ:g} Hz.")
    return "\n".join(out)


# The two channels as built. Verify R2 against your own board — the exported
# netlist in hardware/netlist/ lists R1 = 5.1 kΩ and the two timing capacitors,
# but does not disambiguate the second timing resistor per channel.
CHANNELS = [
    ("channel 1 (fast display)", 5.1e3, 5.1e3, 10e-6),
    ("channel 2 (slow display)", 5.1e3, 5.1e3, 100e-6),
]


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--r1", help="timing resistor R1, e.g. 5.1k")
    p.add_argument("--r2", help="timing resistor R2, e.g. 5.1k")
    p.add_argument("--c", help="timing capacitor, e.g. 10u")
    p.add_argument("--target-hz", type=float, help="solve for R2 at this frequency")
    p.add_argument("--sweep", action="store_true", help="print a capacitor sweep table")
    args = p.parse_args()

    r1 = parse_value(args.r1) if args.r1 else 5.1e3
    r2 = parse_value(args.r2) if args.r2 else 5.1e3
    c = parse_value(args.c) if args.c else 10e-6

    if args.sweep:
        print(sweep(r1, r2))
        return 0

    if args.target_hz:
        try:
            exact = solve_r2(args.target_hz, c, r1)
        except ValueError as exc:
            print(f"error: {exc}")
            return 1
        pick = nearest_e12(exact)
        print(f"Target {args.target_hz} Hz with C = {fmt_c(c)}, R1 = {fmt_r(r1)}")
        print("-" * 46)
        print(f"  R2 required     {fmt_r(exact)}")
        print(f"  nearest E12     {fmt_r(pick)}")
        print()
        print(Astable(r1, pick, c).report("with nearest E12 value"))
        return 0

    if args.r1 or args.r2 or args.c:
        print(Astable(r1, r2, c).report())
        return 0

    for label, cr1, cr2, cc in CHANNELS:
        print(Astable(cr1, cr2, cc).report(label))
        print()

    f1 = Astable(*CHANNELS[0][1:]).frequency
    f2 = Astable(*CHANNELS[1][1:]).frequency
    print("-" * 46)
    print(f"Frequency ratio between channels: {f1 / f2:.1f}x")
    print("This mismatch is the point of the design — the two displays are")
    print("never in phase, so the pair behaves like two independent dice")
    print("rather than one number shown twice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
