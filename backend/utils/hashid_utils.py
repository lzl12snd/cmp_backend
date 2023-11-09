import string

from hashids import Hashids

from backend.settings import get_logger

logger = get_logger()

HASHID_FIELD_MIN_LENGTH = 8

HASHID_FIELD_ALPHABET = string.ascii_uppercase + string.digits  # 大写字母和数字
ALPHABET_REMOVE = "IO"  # 参照车牌规范，去除容易混淆的字母 I 和 O
HASHID_FIELD_ALPHABET = "".join([i for i in HASHID_FIELD_ALPHABET if i not in ALPHABET_REMOVE])


hashids = Hashids(alphabet=HASHID_FIELD_ALPHABET, min_length=HASHID_FIELD_MIN_LENGTH)


def hashid_encode(uid):
    try:
        result = hashids.encode(uid)
        return result
    except Exception as e:
        logger.error(f"hashid 加密失败 uid={uid} error={e}")
        return None


def hashid_decode(hashid_str):
    try:
        hashid_str = str(hashid_str).upper()
        result = hashids.decode(hashid_str)
        if result:
            # logger.info(f"hashid 解密成功 result={result} hashid_str={hashid_str}")
            return result[0]
        return None
    except Exception as e:
        logger.error(f"hashid 解密失败 hashid_str={hashid_str} error={e}")
        return None
