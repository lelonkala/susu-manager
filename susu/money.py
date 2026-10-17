"""Exact money handling.

Amounts are stored as integer pesewas (1 GHS = 100 pesewas), so no floating
point or rounding is ever involved.
"""
from decimal import Decimal, InvalidOperation

PESEWAS_PER_GHS = 100


def parse_ghs(text) -> int:
    """Parse a GHS amount such as '50', '50.5' or '50.00' into pesewas.

    Rejects floats, more than 2 decimal places, and non-numeric input.
    """
    if isinstance(text, float):
        raise ValueError("amounts must be given as strings or ints, not floats")
    try:
        value = Decimal(str(text).strip())
    except InvalidOperation:
        raise ValueError(f"invalid amount: {text!r}") from None
    if not value.is_finite():
        raise ValueError(f"invalid amount: {text!r}")
    pesewas = value * PESEWAS_PER_GHS
    if pesewas != pesewas.to_integral_value():
        raise ValueError("amount cannot have more than 2 decimal places")
    return int(pesewas)


def format_ghs(pesewas: int) -> str:
    """Format pesewas as 'GHS 1,234.50'."""
    sign = "-" if pesewas < 0 else ""
    whole, frac = divmod(abs(pesewas), PESEWAS_PER_GHS)
    return f"{sign}GHS {whole:,}.{frac:02d}"
