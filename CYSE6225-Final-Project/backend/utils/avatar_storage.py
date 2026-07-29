"""Avatar file storage.

Local-disk implementation for dev. To move to S3 for deployment, change only
save_avatar()'s body (upload via boto3 upload_fileobj, return the S3/CloudFront
URL) -- routes and the DB only ever handle a URL string, never a file path.
"""
import os

from config import Config

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _file_size(file_storage) -> int:
    stream = file_storage.stream
    pos = stream.tell()
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(pos)
    return size


def validate_avatar(file_storage) -> str | None:
    """Return an error message if the upload is invalid, else None."""
    if not file_storage or not file_storage.filename:
        return "No file uploaded"
    if _extension(file_storage.filename) not in ALLOWED_EXTENSIONS:
        return "Avatar must be a PNG, JPG, WEBP, or GIF image"
    if _file_size(file_storage) > Config.MAX_AVATAR_BYTES:
        return f"Avatar must be under {Config.MAX_AVATAR_BYTES // (1024 * 1024)}MB"
    return None


def save_avatar(user_id: str, file_storage) -> str:
    """Save the uploaded file, overwriting any previous avatar for this user,
    and return the public URL the frontend should use to display it."""
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

    ext = _extension(file_storage.filename)
    filename = f"{user_id}.{ext}"
    file_storage.save(os.path.join(Config.UPLOAD_DIR, filename))

    # Cache-bust: same filename gets overwritten on every re-upload, so
    # without a changing query param the browser would keep showing the old
    # cached image.
    version = int(os.path.getmtime(os.path.join(Config.UPLOAD_DIR, filename)))
    return f"/api/uploads/avatars/{filename}?v={version}"
