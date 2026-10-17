"""Domain model for one rotating savings group (susu)."""
from __future__ import annotations

from dataclasses import dataclass

from .errors import SusuError


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
