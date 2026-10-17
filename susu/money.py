from decimal import Decimal, InvalidOperation

PESEWAS = 100


def parse_ghs(text) -> int:
    if isinstance(text, float):
        raise ValueError("amounts must be strings or ints, not floats")
    try:
        value = Decimal(str(text).strip()) * PESEWAS
    except InvalidOperation:
        raise ValueError(f"invalid amount: {text!r}") from None
    if not value.is_finite() or value != value.to_integral_value():
        raise ValueError(f"invalid amount (max 2 decimal places): {text!r}")
    return int(value)


def format_ghs(pesewas: int) -> str:
    sign = "-" if pesewas < 0 else ""
    whole, frac = divmod(abs(pesewas), PESEWAS)
    return f"{sign}GHS {whole:,}.{frac:02d}"
