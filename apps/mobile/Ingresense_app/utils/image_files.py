import os
import shutil
import time
from urllib.parse import unquote, urlparse

from kivy.app import App
from kivy.utils import platform


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
    output_path = os.path.join(
        get_image_cache_dir(),
        f"selected_label_{int(time.time() * 1000)}.jpg",
    )

    if platform == "android":
        try:
            return _normalize_with_android_bitmap(source, output_path)
        except Exception as exc:
            print(f"[image_files] Android bitmap normalization failed: {exc}")

    local_source = _resolve_to_local_file(source)

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


def _normalize_with_android_bitmap(source, output_path):
    from jnius import autoclass

    Bitmap = autoclass("android.graphics.Bitmap")
    BitmapFactory = autoclass("android.graphics.BitmapFactory")
    CompressFormat = autoclass("android.graphics.Bitmap$CompressFormat")
    FileOutputStream = autoclass("java.io.FileOutputStream")

    bitmap = None

    try:
        path = _resolve_to_local_file(source)
        orientation = _get_android_exif_orientation(path)
        bitmap = BitmapFactory.decodeFile(path)

        if bitmap is None:
            raise ValueError(f"Android nao conseguiu decodificar a imagem: {source}")

        width = bitmap.getWidth()
        height = bitmap.getHeight()
        max_size = 1800
        largest_side = max(width, height)
        if largest_side > max_size:
            scale = max_size / float(largest_side)
            scaled_width = max(1, int(width * scale))
            scaled_height = max(1, int(height * scale))
            scaled_bitmap = Bitmap.createScaledBitmap(
                bitmap,
                scaled_width,
                scaled_height,
                True,
            )
            bitmap.recycle()
            bitmap = scaled_bitmap

        bitmap = _apply_android_exif_orientation(bitmap, orientation)

        output_stream = FileOutputStream(output_path)
        try:
            compressed = bitmap.compress(CompressFormat.JPEG, 92, output_stream)
            output_stream.flush()
        finally:
            output_stream.close()

        if not compressed:
            raise ValueError("Android nao conseguiu salvar a imagem normalizada.")

        print(f"[image_files] Android bitmap normalized image: {output_path}")
        return output_path
    finally:
        if bitmap is not None:
            bitmap.recycle()


def _get_android_exif_orientation(path):
    try:
        from jnius import autoclass

        ExifInterface = autoclass("android.media.ExifInterface")
        exif = ExifInterface(path)
        return exif.getAttributeInt(
            ExifInterface.TAG_ORIENTATION,
            ExifInterface.ORIENTATION_NORMAL,
        )
    except Exception as exc:
        print(f"[image_files] Could not read Android EXIF orientation: {exc}")
        return 1


def _apply_android_exif_orientation(bitmap, orientation):
    from jnius import autoclass

    Bitmap = autoclass("android.graphics.Bitmap")
    ExifInterface = autoclass("android.media.ExifInterface")
    Matrix = autoclass("android.graphics.Matrix")

    matrix = Matrix()

    if orientation == ExifInterface.ORIENTATION_ROTATE_90:
        matrix.postRotate(90)
    elif orientation == ExifInterface.ORIENTATION_ROTATE_180:
        matrix.postRotate(180)
    elif orientation == ExifInterface.ORIENTATION_ROTATE_270:
        matrix.postRotate(270)
    elif orientation == ExifInterface.ORIENTATION_FLIP_HORIZONTAL:
        matrix.postScale(-1, 1)
    elif orientation == ExifInterface.ORIENTATION_FLIP_VERTICAL:
        matrix.postScale(1, -1)
    elif orientation == ExifInterface.ORIENTATION_TRANSPOSE:
        matrix.postRotate(90)
        matrix.postScale(-1, 1)
    elif orientation == ExifInterface.ORIENTATION_TRANSVERSE:
        matrix.postRotate(270)
        matrix.postScale(-1, 1)
    else:
        return bitmap

    rotated_bitmap = Bitmap.createBitmap(
        bitmap,
        0,
        0,
        bitmap.getWidth(),
        bitmap.getHeight(),
        matrix,
        True,
    )

    if rotated_bitmap != bitmap:
        bitmap.recycle()

    return rotated_bitmap
