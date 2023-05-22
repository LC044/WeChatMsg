import base64
import codecs
import logging
import os
from io import BytesIO

from ..types import Any

logger = logging.getLogger(__name__)

PNG_FORMAT = "png"
JPG_FORMAT = "jpeg"
GIF_FORMAT = "gif"
PDF_FORMAT = "pdf"
SVG_FORMAT = "svg"
EPS_FORMAT = "eps"
B64_FORMAT = "base64"


def make_snapshot(
        engine: Any,
        file_name: str,
        output_name: str,
        delay: float = 2,
        pixel_ratio: int = 2,
        is_remove_html: bool = False,
        **kwargs,
):
    logger.info("Generating file ...")
    file_type = output_name.split(".")[-1]

    content = engine.make_snapshot(
        html_path=file_name,
        file_type=file_type,
        delay=delay,
        pixel_ratio=pixel_ratio,
        **kwargs,
    )
    if file_type in [SVG_FORMAT, B64_FORMAT]:
        save_as_text(content, output_name)
    else:
        # pdf, gif, png, jpeg
        content_array = content.split(",")
        if len(content_array) != 2:
            raise OSError(content_array)

        image_data = decode_base64(content_array[1])

        if file_type in [PDF_FORMAT, GIF_FORMAT, EPS_FORMAT]:
            save_as(image_data, output_name, file_type)
        elif file_type in [PNG_FORMAT, JPG_FORMAT]:
            save_as_png(image_data, output_name)
        else:
            raise TypeError(f"Not supported file type '{file_type}'")

    if "/" not in output_name:
        output_name = os.path.join(os.getcwd(), output_name)

    if is_remove_html and not file_name.startswith("http"):
        os.unlink(file_name)
    logger.info(f"File saved in {output_name}")


def decode_base64(data: str) -> bytes:
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.
    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += "=" * (4 - missing_padding)
    return base64.decodebytes(data.encode("utf-8"))


def save_as_png(image_data: bytes, output_name: str):
    with open(output_name, "wb") as f:
        f.write(image_data)


def save_as_text(image_data: str, output_name: str):
    with codecs.open(output_name, "w", encoding="utf-8") as f:
        f.write(image_data)


def save_as(image_data: bytes, output_name: str, file_type: str):
    try:
        from PIL import Image

        m = Image.open(BytesIO(image_data))
        m.load()
        color = (255, 255, 255)
        b = Image.new("RGB", m.size, color)
        # BUG for Mac:
        #   b.paste(m, mask=m.split()[3])
        b.paste(m)
        b.save(output_name, file_type, quality=100)
    except ModuleNotFoundError:
        raise Exception(f"Please install PIL for {file_type} image type")
