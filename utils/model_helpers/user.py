from ..helper import get_original_hash, get_hash, get_hash_from_memory


def get_picture_hash(picture):
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
