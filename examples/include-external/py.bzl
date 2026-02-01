"Mypy aspect with include_external enabled."

load("@pip_types//:types.bzl", "types")
load("@rules_mypy//mypy:mypy.bzl", "mypy")

mypy_aspect = mypy(
    types = types,
    include_external = True,
)
