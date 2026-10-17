"""Domain model for one rotating savings group (susu)."""
from __future__ import annotations

from dataclasses import dataclass

from .errors import SusuError
from .money import format_ghs


@dataclass(frozen=True)
class Payout:
    week: int
    member: str
    amount: int  # pesewas


class Group:
    def __init__(self, weekly_amount: int):
        if weekly_amount <= 0:
            raise SusuError("weekly contribution must be greater than zero")
        self.weekly_amount = weekly_amount
        self.current_week = 1
        self._members: list[str] = []          # join order = payout order
        self._paid: dict[str, int] = {}        # this week's payments, pesewas
        self.payouts: list[Payout] = []

    # ---- members -------------------------------------------------------
    @property
    def members(self) -> list[str]:
        return list(self._members)

    def _key(self, name: str) -> str:
        return name.strip().casefold()

    def _find(self, name: str) -> str:
        key = self._key(name)
        for m in self._members:
            if self._key(m) == key:
                return m
        raise SusuError(f"unknown member: {name!r}")

    def add_member(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise SusuError("member name cannot be empty")
        if self.started:
            raise SusuError(
                "members can only be added before the first contribution "
                "of week 1 is recorded"
            )
        if any(self._key(m) == self._key(name) for m in self._members):
            raise SusuError(f"duplicate member: {name!r}")
        self._members.append(name)
        self._paid[name] = 0
        return name

    @property
    def started(self) -> bool:
        """The group is locked once any money has been recorded or paid out."""
        return self.current_week > 1 or any(self._paid.values())

    # ---- contributions -------------------------------------------------
    @property
    def finished(self) -> bool:
        """True once every member has received the pot."""
        return bool(self._members) and len(self.payouts) == len(self._members)

    def owed(self, name: str) -> int:
        """Pesewas the member still owes for the current week."""
        return self.weekly_amount - self._paid[self._find(name)]

    def record_contribution(self, name: str, amount: int, week: int | None = None) -> int:
        """Record a (possibly partial) payment; returns the remaining balance."""
        if self.finished:
            raise SusuError("the susu is complete: every member has been paid")
        if week is not None and week != self.current_week:
            raise SusuError(
                f"can only record contributions for the current week "
                f"({self.current_week}), not week {week}"
            )
        member = self._find(name)
        if amount <= 0:
            raise SusuError("amount must be greater than zero")
        owed = self.weekly_amount - self._paid[member]
        if amount > owed:
            raise SusuError(f"{member} only owes {format_ghs(owed)} this week; payment too large")
        self._paid[member] += amount
        return owed - amount

    # ---- closing a week ------------------------------------------------
    def outstanding(self) -> dict[str, int]:
        """Members who still owe for the current week -> pesewas owed."""
        return {m: self.weekly_amount - p for m, p in self._paid.items() if p < self.weekly_amount}

    def close_week(self) -> CloseResult:
        if self.finished:
            raise SusuError("the susu is complete: every member has been paid")
        if not self._members:
            raise SusuError("cannot close a week with no members")
        owing = self.outstanding()
        if owing:
            return CloseResult(closed=False, week=self.current_week, owing=owing)
        recipient = self._members[len(self.payouts)]
        payout = Payout(self.current_week, recipient, self.weekly_amount * len(self._members))
        self.payouts.append(payout)
        self.current_week += 1
        self._paid = {m: 0 for m in self._members}
        return CloseResult(closed=True, week=payout.week, owing={}, payout=payout)

    # ---- report --------------------------------------------------------
    def report(self) -> Report:
        paid_full = [m for m in self._members if self._paid[m] >= self.weekly_amount]
        next_up = None
        if self._members and not self.finished:
            next_up = self._members[len(self.payouts)]
        return Report(
            week=self.current_week,
            finished=self.finished,
            weekly_amount=self.weekly_amount,
            next_recipient=next_up,
            paid_in_full=paid_full,
            owing=self.outstanding(),
            payouts=list(self.payouts),
        )


@dataclass(frozen=True)
class CloseResult:
    closed: bool
    week: int
    owing: dict
    payout: Payout | None = None


@dataclass(frozen=True)
class Report:
    week: int
    finished: bool
    weekly_amount: int
    next_recipient: str | None
    paid_in_full: list
    owing: dict
    payouts: list
