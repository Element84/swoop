import hashlib
import json
from typing import Callable, Dict


def hash_dict(d: Dict, hash_fn: Callable = hashlib.sha1) -> bytes:
    """
    Hashes the values in the transformed payload using the SHA1 algorithm.

    Parameters:
            input (Dict): An input dictionary object that will be hashed
                              using the SHA1 algorithm.
            hash_fn: The type of hashing function to use.

    Returns:
            hashed (bytes): A hash of the input dictionary object.
    """
    return hash_fn(json.dumps(d).encode()).digest()
