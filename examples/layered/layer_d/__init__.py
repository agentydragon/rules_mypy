"""Layer D - depends on layer C."""

from layer_a import LayerAClass
from layer_b import LayerBClass
from layer_c import LayerCClass, get_value_c


def get_value_d() -> int:
    """Return a value computed from layer C."""
    return get_value_c() + 30


class LayerDClass:
    """A class that uses all previous layers."""

    def __init__(self) -> None:
        self.a_instance = LayerAClass(1)
        self.b_instance = LayerBClass()
        self.c_instance = LayerCClass()

    def compute(self) -> int:
        return (
            self.a_instance.compute()
            + self.b_instance.compute()
            + self.c_instance.compute()
            + 10000
        )
