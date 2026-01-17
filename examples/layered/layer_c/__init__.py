"""Layer C - depends on layer B."""

from layer_a import LayerAClass
from layer_b import LayerBClass, get_value_b


def get_value_c() -> int:
    """Return a value computed from layer B."""
    return get_value_b() + 20


class LayerCClass:
    """A class that uses both LayerAClass and LayerBClass."""

    def __init__(self) -> None:
        self.a_instance = LayerAClass(5)
        self.b_instance = LayerBClass()

    def compute(self) -> int:
        return self.a_instance.compute() + self.b_instance.compute() + 1000
