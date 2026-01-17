"""App - top level, depends on all layers."""

from layer_a import LayerAClass, get_value_a
from layer_b import LayerBClass, get_value_b
from layer_c import LayerCClass, get_value_c
from layer_d import LayerDClass, get_value_d


def main() -> None:
    """Main entry point."""
    print(f"Value A: {get_value_a()}")
    print(f"Value B: {get_value_b()}")
    print(f"Value C: {get_value_c()}")
    print(f"Value D: {get_value_d()}")

    d = LayerDClass()
    print(f"Computed: {d.compute()}")


if __name__ == "__main__":
    main()
