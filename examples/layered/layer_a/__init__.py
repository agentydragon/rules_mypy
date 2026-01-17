"""Layer A - base layer with no dependencies."""


def get_value_a() -> int:
    """Return a value from layer A."""
    return 42


class LayerAClass:
    """A class defined in layer A."""

    def __init__(self, value: int) -> None:
        self.value = value

    def compute(self) -> int:
        return self.value * 2
