import io
import os
import random
from asgiref.sync import async_to_sync
from utils.helper import get_original_hash, get_hash, get_hash_from_memory


@async_to_sync
async def get_picture_hash(picture):
    try:
        picture_hash = get_hash_from_memory(picture)
    except:
        try:
            picture_hash = get_hash(picture.url)
        except:
            try:
                picture_hash = get_original_hash(picture.url)
            except:
                picture_hash = None
    return picture_hash

    # blur_hash = await calculate_hash.delay(picture)
    # return blur_hash
    #


def get_default_picture():
    file_path = f"{os.path.abspath(os.getcwd())}/media/avatars/{random.randrange(1, 9)}.png"
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            stream = io.BytesIO(fh.read())
        return stream
