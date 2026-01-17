"Custom py_library rule that also runs mypy."

load("@rules_mypy//mypy:mypy.bzl", "mypy")

mypy_aspect = mypy()
