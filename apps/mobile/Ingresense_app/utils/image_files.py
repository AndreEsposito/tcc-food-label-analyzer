import os
import shutil
import time
from urllib.parse import unquote, urlparse

from kivy.app import App


SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


def get_image_cache_dir():
    """Return a writable app-private directory for selected/captured images."""
    app = App.get_running_app()
    base_dir = app.user_data_dir if app else os.getcwd()
    cache_dir = os.path.join(base_dir, "images")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_capture_path():
    return os.path.join(get_image_cache_dir(), "captured_label.jpg")


def prepare_image_for_app(source):
    """
    Copy and normalize a picked image to a local JPEG Kivy can preview reliably.

    Android gallery providers can return files with unusual metadata, color modes,
    or content URIs. Re-saving as RGB JPEG inside the app storage prevents black
    previews and gives the API a stable file path to upload.
    """
    local_source = _resolve_to_local_file(source)
    output_path = os.path.join(
        get_image_cache_dir(),
        f"selected_label_{int(time.time() * 1000)}.jpg",
    )

    try:
        from PIL import Image, ImageOps

        with Image.open(local_source) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.thumbnail((1800, 1800))
            image.save(output_path, "JPEG", quality=92, optimize=True)
        return output_path
    except Exception as exc:
        print(f"[image_files] Could not normalize image, copying original: {exc}")
        fallback_path = _copy_with_extension(local_source, output_path)
        return fallback_path


def _resolve_to_local_file(source):
    if not source:
        raise ValueError("Imagem nao informada.")

    if source.startswith("content://"):
        return _copy_android_content_uri(source)

    path = _path_from_file_uri(source) if source.startswith("file://") else source
    path = unquote(path)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Imagem nao encontrada: {source}")

    return path


def _path_from_file_uri(uri):
    parsed = urlparse(uri)
    return parsed.path


def _copy_with_extension(source, output_path):
    _, ext = os.path.splitext(source)
    ext = ext.lower() if ext.lower() in SUPPORTED_EXTENSIONS else ".jpg"
    fallback_path = os.path.splitext(output_path)[0] + ext
    shutil.copyfile(source, fallback_path)
    return fallback_path


def _copy_android_content_uri(uri):
    try:
        from jnius import autoclass, jarray
    except Exception as exc:
        raise FileNotFoundError(f"Nao foi possivel ler URI Android: {uri}") from exc

    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Uri = autoclass("android.net.Uri")

    activity = PythonActivity.mActivity
    resolver = activity.getContentResolver()
    input_stream = resolver.openInputStream(Uri.parse(uri))

    if input_stream is None:
        raise FileNotFoundError(f"Nao foi possivel abrir URI Android: {uri}")

    raw_path = os.path.join(
        get_image_cache_dir(),
        f"picked_raw_{int(time.time() * 1000)}.img",
    )

    try:
        with open(raw_path, "wb") as output:
            buffer = jarray("b")([0] * (1024 * 64))
            while True:
                read = input_stream.read(buffer, 0, len(buffer))
                if read == -1:
                    break
                output.write(bytes((byte + 256) % 256 for byte in buffer[:read]))
    finally:
        input_stream.close()

    return raw_path
