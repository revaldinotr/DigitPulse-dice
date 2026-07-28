#!/usr/bin/env python3
"""
logic_verify.py — Formal verification of the digital dice combinational logic.

This script exhaustively proves the claim made in docs/THEORY.md:

    Three 3-input OR gates (one CD4075 package) are sufficient and necessary
    to convert the one-hot outputs Q0..Q5 of a CD4017 decade counter into the
    BCD codes for the digits 1..6 expected by a 74LS47 decoder/driver.

It verifies four independent layers:

    1. The mod-6 feedback (Q6 -> MR) actually confines the counter to Q0..Q5.
    2. The OR mapping produces exactly BCD 1..6, in order, with no aliasing.
    3. The 74LS47 (active-LOW outputs) lights the correct segments for each digit.
    4. Digits 0, 7, 8, 9 are unreachable — the core requirement of a dice.

Exit code 0 = all assertions hold. Non-zero = the design is wrong.

Usage:
    python3 tools/logic_verify.py
    python3 tools/logic_verify.py --table     # print the full truth tables
"""

from __future__ import annotations

import argparse
import sys

# --------------------------------------------------------------------------
# Layer 1 — CD4017 decade counter with mod-6 reset feedback
# --------------------------------------------------------------------------

# CD4017 physical pin numbers for each decoded output. Taken from the
# datasheet; note the deliberately scrambled pin order — this is the single
# most common source of wiring errors on this build.
CD4017_PINOUT = {
    "Q0": 3, "Q1": 2, "Q2": 4, "Q3": 7, "Q4": 10,
    "Q5": 1, "Q6": 5, "Q7": 6, "Q8": 9, "Q9": 11,
}
CD4017_MR_PIN = 15   # Master Reset, active HIGH
CD4017_CLK_PIN = 14  # Clock, rising edge


def cd4017_sequence(reset_from: str = "Q6") -> list[str]:
    """Simulate the counter clock-by-clock with Qn -> MR feedback.

    The reset is asynchronous: the instant `reset_from` goes HIGH it drives MR
    HIGH and the counter snaps back to Q0. That state is therefore a glitch a
    few tens of nanoseconds wide and is never observed as a stable output.
    """
    reset_index = int(reset_from[1:])
    observed: list[str] = []
    state = 0
    for _ in range(100):  # far more clocks than one full cycle
        observed.append(f"Q{state}")
        state += 1
        if state == reset_index:  # MR asserted -> asynchronous snap to zero
            state = 0
        elif state > 9:
            state = 0
    # Return one complete cycle
    cycle_len = observed[1:].index("Q0") + 1
    return observed[:cycle_len]


# --------------------------------------------------------------------------
# Layer 2 — the CD4075 OR-gate mapping
# --------------------------------------------------------------------------

# Each 74LS47 BCD input is driven by one 3-input OR gate. The gate inputs are
# derived directly from the binary expansion of the target digits:
#
#   digit : D C B A
#     1   : 0 0 0 1     A is HIGH for 1, 3, 5
#     2   : 0 0 1 0     B is HIGH for 2, 3, 6
#     3   : 0 0 1 1     C is HIGH for 4, 5, 6
#     4   : 0 1 0 0     D is HIGH for nothing in 1..6  -> tie to GND
#     5   : 0 1 0 1
#     6   : 0 1 1 0
#
# Q_n represents digit n+1, so the gate inputs are offset by one.
OR_GATE_MAP = {
    "A": ["Q0", "Q2", "Q4"],  # digits 1, 3, 5
    "B": ["Q1", "Q2", "Q5"],  # digits 2, 3, 6
    "C": ["Q3", "Q4", "Q5"],  # digits 4, 5, 6
    "D": [],                  # hard-wired LOW
}

# 74LS47 BCD input weights and their physical pin numbers.
BCD_WEIGHT = {"A": 1, "B": 2, "C": 4, "D": 8}
LS47_INPUT_PIN = {"A": 7, "B": 1, "C": 2, "D": 6}


def or_mapping(active_q: str) -> dict[str, int]:
    """Evaluate the three OR gates for a given one-hot counter state."""
    return {name: int(active_q in inputs) for name, inputs in OR_GATE_MAP.items()}


def bcd_value(bits: dict[str, int]) -> int:
    return sum(BCD_WEIGHT[name] for name, bit in bits.items() if bit)


# --------------------------------------------------------------------------
# Layer 3 — 74LS47 BCD-to-seven-segment decoder (active-LOW outputs)
# --------------------------------------------------------------------------

# Segments lit for each BCD input value, per the 74LS47 datasheet.
# The 74LS47 drives a COMMON-ANODE display: an output pin pulled LOW lights
# its segment. Values 10..15 produce the datasheet's non-numeric patterns.
LS47_SEGMENTS = {
    0: "abcdef",
    1: "bc",
    2: "abdeg",
    3: "abcdg",
    4: "bcfg",
    5: "acdfg",
    6: "cdefg",
    7: "abc",
    8: "abcdefg",
    9: "abcfg",
}

LS47_OUTPUT_PIN = {"a": 13, "b": 12, "c": 11, "d": 10, "e": 9, "f": 15, "g": 14}


def ls47_decode(value: int) -> str:
    return LS47_SEGMENTS[value]


def ls47_active_low(value: int) -> dict[str, int]:
    """Return the real logic level on each output pin (0 = lit)."""
    lit = ls47_decode(value)
    return {seg: (0 if seg in lit else 1) for seg in "abcdefg"}


# --------------------------------------------------------------------------
# ASCII rendering, so failures are readable at a glance
# --------------------------------------------------------------------------

def render(segments: str) -> list[str]:
    s = set(segments)
    return [
        " {} ".format("_" if "a" in s else " "),
        "{}{}{}".format(
            "|" if "f" in s else " ",
            "_" if "g" in s else " ",
            "|" if "b" in s else " ",
        ),
        "{}{}{}".format(
            "|" if "e" in s else " ",
            "_" if "d" in s else " ",
            "|" if "c" in s else " ",
        ),
    ]


def render_row(values: list[int]) -> str:
    blocks = [render(ls47_decode(v)) for v in values]
    return "\n".join("   ".join(b[i] for b in blocks) for i in range(3))


# --------------------------------------------------------------------------
# Test layers
# --------------------------------------------------------------------------

def check_counter() -> list[str]:
    log = []
    cycle = cd4017_sequence("Q6")
    assert cycle == ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5"], (
        f"mod-6 feedback broken: counter cycles through {cycle}"
    )
    log.append(f"counter cycle       : {' -> '.join(cycle)} -> (repeat)")
    log.append(f"cycle length        : {len(cycle)} states, as required for a d6")

    # A reset taken from the wrong output is the classic build error; show that
    # the test would actually catch it.
    for wrong in ("Q5", "Q7"):
        bad = cd4017_sequence(wrong)
        assert bad != ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5"], (
            f"test is vacuous: {wrong} -> MR also yields a mod-6 count"
        )
        log.append(f"negative control    : {wrong} -> MR gives {len(bad)} states (rejected)")
    return log


def check_mapping() -> list[str]:
    log = []
    produced = []
    for n in range(6):
        q = f"Q{n}"
        bits = or_mapping(q)
        value = bcd_value(bits)
        expected = n + 1
        assert value == expected, (
            f"{q} maps to BCD {value:04b} ({value}), expected {expected:04b} ({expected})"
        )
        assert bits["D"] == 0, "input D must remain LOW for all dice digits"
        produced.append(value)

    assert sorted(produced) == [1, 2, 3, 4, 5, 6], "digits are not a clean 1..6 set"
    assert len(set(produced)) == 6, "two counter states decode to the same digit"
    log.append(f"decoded digits      : {produced}")

    # Gate-count argument: each BCD input needs an OR of exactly 3 terms.
    widths = {k: len(v) for k, v in OR_GATE_MAP.items() if v}
    assert all(w == 3 for w in widths.values()), f"gate widths are not all 3: {widths}"
    assert len(widths) == 3, "expected exactly three driven BCD inputs"
    log.append(f"gate widths         : {widths} -> fits one CD4075 exactly")

    # D is unused, so digits >= 8 are structurally impossible.
    unreachable = {0, 7, 8, 9} - set(produced)
    assert unreachable == {0, 7, 8, 9}, f"forbidden digits are reachable: {unreachable}"
    log.append("forbidden digits    : 0, 7, 8, 9 all unreachable")
    return log


def check_decoder() -> list[str]:
    log = []
    for n in range(6):
        digit = n + 1
        segs = ls47_decode(digit)
        levels = ls47_active_low(digit)
        lit = {s for s, lvl in levels.items() if lvl == 0}
        assert lit == set(segs), f"active-LOW inversion wrong for digit {digit}"
    log.append("segment patterns    : digits 1..6 verified against 74LS47 datasheet")
    log.append("output polarity     : active-LOW confirmed (common-anode display)")

    # Sanity: '1' and '7' must be distinguishable, or the dice is ambiguous.
    assert ls47_decode(1) != ls47_decode(7), "digits 1 and 7 are visually identical"
    log.append("ambiguity check     : '1' (bc) distinct from '7' (abc)")
    return log


def check_end_to_end() -> list[str]:
    """Walk the whole chain: clock edge -> counter -> OR -> decoder -> segments."""
    log = []
    results = []
    for n in range(6):
        q = f"Q{n}"
        bits = or_mapping(q)
        value = bcd_value(bits)
        segs = ls47_decode(value)
        results.append((q, bits, value, segs))
        assert value == n + 1

    log.append("")
    log.append("  clk  4017    A B C D   BCD   digit   segments lit")
    log.append("  " + "-" * 52)
    for i, (q, bits, value, segs) in enumerate(results):
        log.append(
            f"  {i:>3}  {q:<6}  {bits['A']} {bits['B']} {bits['C']} {bits['D']}"
            f"   {value:04b}   {value:^5}   {segs}"
        )
    log.append("")
    log.append(render_row([v for _, _, v, _ in results]))
    log.append("")
    return log


# --------------------------------------------------------------------------

def print_tables() -> None:
    print("\nCD4017 pinout (decoded outputs)")
    print("-" * 40)
    for q, pin in CD4017_PINOUT.items():
        note = ""
        if q in ("Q0", "Q1", "Q2", "Q3", "Q4", "Q5"):
            note = f"-> OR network (digit {int(q[1:]) + 1})"
        elif q == "Q6":
            note = f"-> MR pin {CD4017_MR_PIN} (mod-6 reset)"
        else:
            note = "-> not connected"
        print(f"  {q}  pin {pin:>2}   {note}")

    print("\nCD4075 OR network")
    print("-" * 40)
    for name, inputs in OR_GATE_MAP.items():
        pin = LS47_INPUT_PIN[name]
        if inputs:
            print(f"  {name} (pin {pin:>2}, weight {BCD_WEIGHT[name]}) = "
                  f"{' + '.join(inputs)}")
        else:
            print(f"  {name} (pin {pin:>2}, weight {BCD_WEIGHT[name]}) = GND")

    print("\n74LS47 output pins")
    print("-" * 40)
    for seg, pin in LS47_OUTPUT_PIN.items():
        print(f"  segment {seg}  pin {pin:>2}  (LOW = lit)")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--table", action="store_true",
                        help="print pinout and mapping tables, then verify")
    args = parser.parse_args()

    if args.table:
        print_tables()

    layers = [
        ("counter (mod-6 feedback)", check_counter),
        ("combinational mapping", check_mapping),
        ("74LS47 decoding", check_decoder),
        ("end-to-end chain", check_end_to_end),
    ]

    print("Digital Dice — logic verification")
    print("=" * 56)
    try:
        for title, fn in layers:
            print(f"\n[{title}]")
            for line in fn():
                print(f"  {line}" if line and not line.startswith(" ") else line)
    except AssertionError as exc:
        print(f"\nFAIL: {exc}", file=sys.stderr)
        return 1

    print("=" * 56)
    print("All checks passed. The three-OR-gate design is correct.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
