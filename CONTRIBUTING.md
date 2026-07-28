# Contributing

This is an academic project from Politeknik Negeri Sriwijaya, published so
that others can build it, learn from it, and correct it. Contributions are
welcome — particularly from anyone who has actually built the circuit.

## What is most useful

**Corrections.** If you built this and something in the documentation is
wrong, that is the most valuable thing you can report. The netlist reference
was transcribed from a schematic export that does not annotate every resistor
per channel, and several values are marked "verify" for exactly that reason.
Measured values from a real board beat inferred ones.

**Build reports.** What worked, what did not, what took longest to debug.
Faults that recur belong in
[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md), which is ordered by how
often each one actually happens — that ordering is only as good as the data
behind it.

**Photographs.** Clear photos of a working build, particularly of the wiring
between the CD4017 and CD4075, help more than any amount of prose.

**Schematic source files.** The repository currently ships a PDF export. A
KiCad, EasyEDA or Proteus source file would let people modify the design
rather than redraw it.

## Ground rules

**Verify before you claim.** If a change touches the logic, run the verifier:

```bash
python3 tools/logic_verify.py --table
```

It must exit 0. CI runs it on every pull request against Python 3.9 and 3.12,
and also confirms that the verifier itself still fails on a deliberately
broken mapping — a test suite that cannot fail proves nothing.

**Keep documented errors documented.** The 12 V supply in the original
proposal is wrong, and the repository says so in
[docs/BOM.md](docs/BOM.md#supply-voltage) rather than quietly printing 5 V.
The same goes for the spin-rate analysis. If you find another error, add it
to the record — do not erase the original.

**Both READMEs, or neither.** `README.md` (English) and `README.id.md`
(Indonesian) mirror each other. A change to one needs the same change to the
other, or the two drift apart.

**No microcontroller ports in this repository.** An ATtiny version of this
project is a fine thing to build, but it demonstrates none of the digital
logic that is the point here. Fork it and link back.

## How to submit

1. Fork the repository
2. Create a branch: `git checkout -b fix/segment-resistor-value`
3. Make the change and run `python3 tools/logic_verify.py`
4. Commit with a message that says what changed and why
5. Open a pull request describing what you built or measured

## Reporting a build problem

Use the [build problem issue template](.github/ISSUE_TEMPLATE/build-problem.md).
Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) first — the phantom
`7`, inverted digits, and intermittent skipping are all covered there with
their causes.

## Attribution

This is coursework. Please cite the authors if you build on it — see
[LICENSE](LICENSE) for the citation format.
