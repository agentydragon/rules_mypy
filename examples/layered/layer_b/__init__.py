"""Layer B - depends on layer A."""

from layer_a import LayerAClass, get_value_a


def get_value_b() -> int:
    """Return a value computed from layer A."""
    return get_value_a() + 10


class LayerBClass:
    """A class that uses LayerAClass."""

    def __init__(self) -> None:
        self.a_instance = LayerAClass(get_value_a())

    def compute(self) -> int:
        return self.a_instance.compute() + 100
