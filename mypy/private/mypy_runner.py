import argparse
import contextlib
import pathlib
import os
import shutil
import sys
import tempfile
from typing import Any, Generator, Optional

import mypy.api
import mypy.util


# Cache for symlink availability check (None = not tested, True/False = result)
_symlinks_supported: Optional[bool] = None


def _can_symlink() -> bool:
    """
    Test if symlinks are supported on this system.

    On Windows, symlinks require either:
    - Developer Mode enabled (Windows 10 1703+)
    - Running as Administrator

    This mirrors Bazel's --windows_enable_symlinks behavior.
    """
    global _symlinks_supported
    if _symlinks_supported is not None:
        return _symlinks_supported

    # Try to create a test symlink
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_target = pathlib.Path(tmpdir) / "target"
            test_link = pathlib.Path(tmpdir) / "link"
            test_target.write_text("test")
            test_link.symlink_to(test_target)
            _symlinks_supported = test_link.is_symlink()
    except (OSError, NotImplementedError):
        _symlinks_supported = False

    return _symlinks_supported


def _link_or_copy(src: pathlib.Path, dst: pathlib.Path) -> None:
    """
    Create a symlink from dst to src, falling back to copy if symlinks aren't supported.

    This mirrors Bazel's approach where symlinks are preferred for efficiency,
    but copies are used as fallback on systems where symlinks aren't available
    (e.g., Windows without Developer Mode).
    """
    if _can_symlink():
        dst.symlink_to(src.resolve())
    else:
        shutil.copy(src, dst)


def _merge_upstream_caches(cache_dir: str, upstream_caches: list[str]) -> None:
    current = pathlib.Path(cache_dir)
    current.mkdir(parents=True, exist_ok=True)

    for upstream_dir in upstream_caches:
        upstream = pathlib.Path(upstream_dir)

        # TODO(mark): maybe there's a more efficient way to synchronize the cache dirs?
        for dirpath_str, _, filenames in os.walk(upstream.as_posix()):
            dirpath = pathlib.Path(dirpath_str)
            relative_dir = dirpath.relative_to(upstream)
            for file in filenames:
                upstream_path = dirpath / file
                target_path = current / relative_dir / file
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if not target_path.exists():
                    # Use symlink to save disk space, with copy fallback for Windows
                    _link_or_copy(upstream_path, target_path)

    # missing_stubs is mutable, so remove it
    missing_stubs = current / "missing_stubs"
    if missing_stubs.exists():
        missing_stubs.unlink()


@contextlib.contextmanager
def managed_cache_dir(
    cache_dir: Optional[str], upstream_caches: list[str]
) -> Generator[str, Any, Any]:
    """
    Returns a managed cache directory.

    When cache_dir exists, returns a merged view of cache_dir with upstream_caches.
    Otherwise, returns a temporary directory that will be cleaned up when the resource
    is released.
    """
    if cache_dir:
        _merge_upstream_caches(cache_dir, list(upstream_caches))
        yield cache_dir
    else:
        tmpdir = tempfile.TemporaryDirectory()
        yield tmpdir.name
        tmpdir.cleanup()


def run_mypy(
    mypy_ini: Optional[str], cache_dir: str, srcs: list[str]
) -> tuple[str, str, int]:
    maybe_config = ["--config-file", mypy_ini] if mypy_ini else []
    report, errors, status = mypy.api.run(
        maybe_config
        + [
            # do not check mtime in cache
            "--skip-cache-mtime-checks",
            # mypy defaults to incremental, but force it on anyway
            "--incremental",
            # use a known cache-dir
            f"--cache-dir={cache_dir}",
            # use current dir + MYPYPATH to resolve deps
            "--explicit-package-bases",
            # speedup
            "--fast-module-lookup",
        ]
        + srcs
    )
    if status:
        sys.stderr.write(errors)
        sys.stderr.write(report)

    return report, errors, status


def run(
    output: Optional[str],
    cache_dir: Optional[str],
    upstream_caches: list[str],
    mypy_ini: Optional[str],
    srcs: list[str],
) -> None:
    if len(srcs) > 0:
        with managed_cache_dir(cache_dir, upstream_caches) as cache_dir:
            report, errors, status = run_mypy(mypy_ini, cache_dir, srcs)
    else:
        report, errors, status = "", "", 0

    if output:
        with open(output, "w+") as file:
            file.write(errors)
            file.write(report)

    # use mypy's hard_exit to exit without freeing objects, it can be meaningfully
    # faster than an orderly shutdown
    mypy.util.hard_exit(status)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=False)
    parser.add_argument("-c", "--cache-dir", required=False)
    parser.add_argument("--upstream-cache", required=False, action="append")
    parser.add_argument("--mypy-ini", required=False)
    parser.add_argument("src", nargs="*")
    args = parser.parse_args()

    output: Optional[str] = args.output
    cache_dir: Optional[str] = args.cache_dir
    upstream_cache: list[str] = args.upstream_cache or []
    mypy_ini: Optional[str] = args.mypy_ini
    srcs: list[str] = args.src

    run(output, cache_dir, upstream_cache, mypy_ini, srcs)


if __name__ == "__main__":
    main()
