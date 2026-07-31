"""Avatar file storage — S3-backed, served through CloudFront.

Instances behind an ALB/ASG are ephemeral and don't share local disk, so
avatars can't live on the instance filesystem: an upload landing on one
instance would be invisible to users routed to another, and would vanish
entirely on the next Instance Refresh. S3 is the shared, durable store;
CloudFront (with Origin Access Control) is what the browser actually loads
the image from -- the bucket itself is not publicly readable.
"""
import time

import boto3

from config import Config

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

_s3 = boto3.client("s3", region_name=Config.AWS_REGION)


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _file_size(file_storage) -> int:
    stream = file_storage.stream
    pos = stream.tell()
    stream.seek(0, 2)  # SEEK_END
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
    """Upload to S3, overwriting any previous avatar for this user, and
    return the CloudFront URL the frontend should use to display it."""
    ext = _extension(file_storage.filename)
    key = f"avatars/{user_id}.{ext}"
    content_type = file_storage.mimetype or f"image/{'jpeg' if ext == 'jpg' else ext}"

    _s3.upload_fileobj(
        file_storage,
        Config.AVATAR_BUCKET,
        key,
        ExtraArgs={"ContentType": content_type},
    )

    # Cache-bust: same key gets overwritten on every re-upload, so without a
    # changing query param CloudFront/the browser would keep serving the
    # cached previous image.
    version = int(time.time())
    return f"{Config.AVATAR_CDN_BASE_URL}/{key}?v={version}"
