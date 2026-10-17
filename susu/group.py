from __future__ import annotations

from dataclasses import dataclass

from .errors import SusuError
from .money import format_ghs


@dataclass(frozen=True)
class Payout:
    week: int
    member: str
    amount: int


@dataclass(frozen=True)
class CloseResult:
    closed: bool
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


class Group:
    def __init__(self, weekly_amount: int):
        if weekly_amount <= 0:
            raise SusuError("weekly contribution must be greater than zero")
        self.weekly_amount = weekly_amount
        self.current_week = 1
        self.payouts: list[Payout] = []
        self._paid: dict[str, int] = {}  # insertion order = join order

    @property
    def members(self) -> list[str]:
        return list(self._paid)

    @property
    def started(self) -> bool:
        return self.current_week > 1 or any(self._paid.values())

    @property
    def finished(self) -> bool:
        return bool(self._paid) and len(self.payouts) == len(self._paid)

    def _find(self, name: str) -> str:
        for member in self._paid:
            if member.casefold() == name.strip().casefold():
                return member
        raise SusuError(f"unknown member: {name!r}")

    def add_member(self, name: str) -> str:
        name = name.strip()
        if not name:
            raise SusuError("member name cannot be empty")
        if self.started:
            raise SusuError("members can only be added before any contribution is recorded")
        if any(m.casefold() == name.casefold() for m in self._paid):
            raise SusuError(f"duplicate member: {name!r}")
        self._paid[name] = 0
        return name

    def owed(self, name: str) -> int:
        return self.weekly_amount - self._paid[self._find(name)]

    def record_contribution(self, name: str, amount: int, week: int | None = None) -> int:
        self._ensure_open()
        if week is not None and week != self.current_week:
            raise SusuError(f"only the current week ({self.current_week}) accepts contributions")
        member = self._find(name)
        if amount <= 0:
            raise SusuError("amount must be greater than zero")
        owed = self.owed(member)
        if amount > owed:
            raise SusuError(f"{member} only owes {format_ghs(owed)} this week")
        self._paid[member] += amount
        return owed - amount

    def outstanding(self) -> dict[str, int]:
        return {m: self.weekly_amount - p for m, p in self._paid.items() if p < self.weekly_amount}

    def close_week(self) -> CloseResult:
        self._ensure_open()
        if not self._paid:
            raise SusuError("cannot close a week with no members")
        owing = self.outstanding()
        if owing:
            return CloseResult(False, owing)
        payout = Payout(self.current_week, self.members[len(self.payouts)],
                        self.weekly_amount * len(self._paid))
        self.payouts.append(payout)
        self.current_week += 1
        self._paid = dict.fromkeys(self._paid, 0)
        return CloseResult(True, {}, payout)

    def report(self) -> Report:
        full = [m for m, p in self._paid.items() if p >= self.weekly_amount]
        upcoming = None if self.finished or not self._paid else self.members[len(self.payouts)]
        return Report(self.current_week, self.finished, self.weekly_amount, upcoming,
                      full, self.outstanding(), list(self.payouts))

    def _ensure_open(self) -> None:
        if self.finished:
            raise SusuError("the susu is complete: every member has been paid")
