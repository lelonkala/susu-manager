from __future__ import annotations

import shlex

from .errors import SusuError
from .group import Group, Report
from .money import format_ghs, parse_ghs

HELP = """Commands:
  new <weekly_amount>            create a group (e.g. new 50.00)
  add <name>                     add a member (before any payment is recorded)
  pay <name> <amount> [week]     record a contribution for the current week
  close                          close the week: pay out if all paid in full
  report                         show current week, balances and payout history
  help | quit"""


def render_report(r: Report) -> str:
    lines = [f"Week {r.week} | weekly contribution {format_ghs(r.weekly_amount)}"]
    if r.finished:
        lines.append("Cycle complete: every member has received the pot.")
    elif r.next_recipient:
        lines.append(f"Next recipient: {r.next_recipient}")
    lines.append("Paid in full: " + (", ".join(r.paid_in_full) or "nobody"))
    if r.owing:
        lines.append("Owing:")
        lines += [f"  {m} owes {format_ghs(a)}" for m, a in r.owing.items()]
    else:
        lines.append("Owing: nobody")
    lines.append("Payout history:")
    lines += [f"  Week {p.week}: {p.member} received {format_ghs(p.amount)}" for p in r.payouts] or ["  (none yet)"]
    return "\n".join(lines)


class Shell:
    def __init__(self):
        self.group: Group | None = None

    def _need_group(self) -> Group:
        if self.group is None:
            raise SusuError("no group yet: use 'new <weekly_amount>' first")
        return self.group

    def execute(self, line: str) -> str:
        parts = shlex.split(line)
        if not parts:
            return ""
        cmd, args = parts[0].lower(), parts[1:]
        try:
            return self._dispatch(cmd, args)
        except (SusuError, ValueError) as e:
            return f"Error: {e}"

    def _dispatch(self, cmd: str, args: list[str]) -> str:
        if cmd == "help":
            return HELP
        if cmd == "new":
            self._arity(args, 1, 1, "new <weekly_amount>")
            self.group = Group(parse_ghs(args[0]))
            return f"Group created. Weekly contribution: {format_ghs(self.group.weekly_amount)}"
        g = self._need_group()
        if cmd == "add":
            self._arity(args, 1, 1, "add <name>")
            return f"Added {g.add_member(args[0])} (position {len(g.members)})"
        if cmd == "pay":
            self._arity(args, 2, 3, "pay <name> <amount> [week]")
            week = int(args[2]) if len(args) == 3 else None
            left = g.record_contribution(args[0], parse_ghs(args[1]), week)
            return f"Recorded. {args[0]} still owes {format_ghs(left)} this week."
        if cmd == "close":
            res = g.close_week()
            if res.closed:
                p = res.payout
                return (f"Week {p.week} closed. {p.member} receives {format_ghs(p.amount)}."
                        + ("\nAll members have been paid; the cycle is complete."
                           if g.finished else f"\nWeek {g.current_week} begins."))
            return "Week not closed:\n" + "\n".join(
                f"{m} owes {format_ghs(a)}" for m, a in res.owing.items())
        if cmd == "report":
            return render_report(g.report())
        return f"Unknown command {cmd!r}. Type 'help'."

    @staticmethod
    def _arity(args, lo, hi, usage):
        if not lo <= len(args) <= hi:
            raise SusuError(f"usage: {usage}")


def main() -> None:
    shell = Shell()
    print("Susu manager. Type 'help' for commands.")
    while True:
        try:
            line = input("susu> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip().lower() in ("quit", "exit"):
            break
        try:
            out = shell.execute(line)
        except ValueError as e:
            out = f"Error: {e}"
        if out:
            print(out)
