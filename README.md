# Susu – rotating savings group manager

A small Python (3.10+, standard library only) command-line program that manages one susu group in GHS.

## Run

```bash
python -m susu
```

This opens an interactive shell:

| Command | Meaning |
|---|---|
| `new <weekly_amount>` | Create the group, e.g. `new 50.00` |
| `add <name>` | Add a member (quote names with spaces: `add "Esi Mensah"`) |
| `pay <name> <amount> [week]` | Record a full or partial contribution |
| `close` | Close the week: pays the pot if everyone paid in full, otherwise lists who owes what |
| `report` | Current week, who paid, who owes, payout history |
| `help`, `quit` | |

Example session (the scenario from the brief):

```
susu> new 50
susu> add Ama
susu> add Kofi
susu> add Esi
susu> pay Ama 50
susu> pay Kofi 50
susu> pay Esi 30
susu> close
Week not closed:
Esi owes GHS 20.00
susu> pay Esi 20
susu> close
Week 1 closed. Ama receives GHS 150.00.
Week 2 begins.
```

## Tests

```bash
python -m unittest -v
```

## Layout

- `susu/money.py` – exact money: parsing/formatting using integer pesewas
- `susu/group.py` – domain rules (members, contributions, closing weeks, report data); no I/O
- `susu/cli.py` – command parsing and text rendering
- `tests/` – unit tests for each layer

Assumptions and design decisions are in [NOTES.md](NOTES.md).
