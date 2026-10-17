# Notes

## Assumptions / rules I chose
1. **Members are locked once money moves.** Members can be added only until the first contribution of week 1 is recorded. Adding later would make the payout order and "everyone paid" unfair (someone could join after others already funded pots). Payout order = join order.
2. **Contributions only for the current week.** `week` is optional on `pay`; if given it must equal the current week. Past weeks are closed; future weeks can't be pre-paid (this also keeps overpayment validation simple: "owed" is always defined against one week).
3. **Cycle length = number of members.** After every member has received the pot, the susu is complete and further payments/closes are rejected (a new group would be started).
4. **Pot = weekly amount × number of members**, which equals the sum of contributions, since a week only closes when everyone has paid in full.
5. **Names** are trimmed and compared case-insensitively (`Ama` and `ama` are the same member); the original spelling is kept for display.
6. A group needs at least one member before a week can close; a weekly amount must be > 0.
7. Closing a week that can't close changes nothing; it just reports arrears. Partial payments persist across attempts to close.

## Decisions
- **Money is integer pesewas**, parsed with `Decimal` from strings. Floats are rejected, as is more than 2 decimal places, so there is no rounding anywhere.
- **Domain separated from I/O**: `Group` raises `SusuError` for rule violations and returns data (`CloseResult`, `Report`); the CLI only parses and formats. Failed operations never partially mutate state (validate first, then change).
- **Interactive shell** rather than one-shot commands, because state is in memory and a REPL needs no persistence layer.
- Standard library only (`unittest`) so there is nothing to install.

## With more time
- Persist state (JSON/SQLite) so the CLI could be used one command at a time and survive restarts.
- Keep a history of past weeks' contributions (audit trail) and allow corrections/refunds.
- Support late joiners with a defined catch-up rule, and starting a new cycle after completion.
- Configurable payout order (e.g. draw lots) and per-member missed-payment tracking.
- More tests for the CLI edge cases (quoting, bad arguments) and property-based tests for money invariants.
