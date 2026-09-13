import atexit
import base64
import os
import sys
import pytest


def warp_to(direct_vm, iso_timestamp: str) -> None:
    direct_vm.warp(iso_timestamp)
    gl = sys.modules.get("genlayer.gl")
    if gl is None:
        return
    raw = getattr(gl, "message_raw", None)
    if isinstance(raw, dict):
        raw["datetime"] = iso_timestamp
    message = getattr(gl, "message", None)
    nested = getattr(message, "raw", None)
    if isinstance(nested, dict):
        nested["datetime"] = iso_timestamp


@pytest.fixture(autouse=True)
def _reset_contract_registry():
    yield
    try:
        import genlayer.gl.genvm_contracts as contracts
    except ImportError:
        return
    contracts.__known_contract__ = None


if sys.platform == "win32":
    from gltest.direct import loader as _loader
    from gltest.direct import wasi_mock as _wasi
    _leaked = []
    _unlink = os.unlink

    def _tolerant(path, *args, **kwargs):
        try:
            return _unlink(path, *args, **kwargs)
        except PermissionError:
            _leaked.append(os.fspath(path))

    _original = _loader._inject_message_to_fd0

    def _inject(vm):
        os.unlink = _tolerant
        try:
            return _original(vm)
        finally:
            os.unlink = _unlink

    _loader._inject_message_to_fd0 = _inject
    _render = _wasi._handle_web_render
    _png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")

    def _image_render(vm, data):
        result = _render(vm, data)
        if data.get("mode") == "screenshot" and result.get("ok", {}).get("image") == b"":
            result["ok"]["image"] = _png
        return result

    _wasi._handle_web_render = _image_render

    @atexit.register
    def _sweep():
        for path in _leaked:
            try:
                _unlink(path)
            except OSError:
                pass

# The screenshot decoder requires valid image bytes on every platform. The
# Direct Mode renderer otherwise returns an empty placeholder for mocked
# screenshots, which is not a semantic test failure and breaks Linux CI.
if sys.platform != "win32":
    from gltest.direct import wasi_mock as _linux_wasi
    _linux_render = _linux_wasi._handle_web_render
    _linux_png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")

    def _linux_image_render(vm, data):
        result = _linux_render(vm, data)
        if data.get("mode") == "screenshot" and result.get("ok", {}).get("image") == b"":
            result["ok"]["image"] = _linux_png
        return result

    _linux_wasi._handle_web_render = _linux_image_render
