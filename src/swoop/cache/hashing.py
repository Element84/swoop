from copy import deepcopy
import hashlib
import json
import re
from typing import Dict, List, Optional, Union


def hash(input: Dict, hash_fn: Optional[object] = hashlib.sha1) -> bytes:
    """
    Hashes the values in the transformed payload using the SHA1 algorithm.

    Parameters:
            input (Dict): An input dictionary object that will be hashed
                              using the SHA1 algorithm.
            hash_fn: The type of hashing function to use.

    Returns:
            hashed (bytes): A hash of the input dictionary object.
    """
    sha = hash_fn()
    sha.update(json.dumps(input).encode())
    hashed = sha.digest()
    return hashed


def traverse(dict_or_list: Union[Dict, List], path: List = []):
    """
    Traverses the entire payload object to yield a list of paths to all nodes.

    Parameters:
            payload (Dict): The input payload whose keys will be ordered
                            alphabetically.

    Returns:
            result (Dict): The input payload with keys (including nested)
                           ordered alphabetically.
    """
    if isinstance(dict_or_list, dict):
        iterator = sorted(dict_or_list.items())
    else:
        iterator = enumerate(dict_or_list)
    for k, v in iterator:
        yield path + [k], v,
        if isinstance(v, (dict, list)):
            yield from traverse(v, path + [k])


def filter_path_list(expressions: List[str], path_list: List[str]) -> List[str]:
    """
    Finds the paths in the path list that match the expressions in
    a list of expressions written in dot notation.

    Parameters:
            expressions (List[str]): A list of expressions written in dot notation
                that we want to evaluate
            path_list (List[str]): A list of all paths to all nodes in the input
                                   payload

    Returns:
            match_list (str): A list of paths in the path_list that match
            with the expressions in the expressions list.
    """

    match_list = []

    for exp in expressions:
        regex = []
        split_exp = exp.split(".")
        for e in split_exp:
            if "[" in e:
                sub = e.split("[")
                if "[*]" in e:
                    regex.append(sub[0] + ".\\d+")
            else:
                regex.append(e)
        reg_join = ".".join(regex)
        r = re.compile(reg_join)
        match_list += list(filter(r.match, path_list))
    return match_list


def include_paths(payload: Dict, process_list: List[str]) -> Dict:
    """
    Keeps the paths in the payload that are included.

    Parameters:
            payload (Dict): The input payload object.
            process_list (List[str]): A list of the paths in the input payload
                                      that need to be kept.

    Returns:
            out_payload (Dict): A dictionary object that contains just the paths
                                that are included.
    """

    out_payload = {}

    inc_payload = deepcopy(payload)

    for i in range(len(process_list)):
        here = inc_payload
        here_out = out_payload
        key_string = process_list[i]
        keys = key_string.split(".")

        for i in range(len(keys)):
            curr_key = keys[i]

            if curr_key.isnumeric():
                curr_key = int(curr_key)
                here = here[curr_key]
                if type(here) == dict:
                    if curr_key >= len(here_out):
                        here_out.append({})
                    here_out = here_out[curr_key]
                elif type(here) == list:
                    here_out.append([])
                    here_out[curr_key] = []
                    here_out = here_out[curr_key]
                else:
                    if type(here_out) == dict:
                        here_out[curr_key] = here
                    elif type(here_out) == list:
                        here_out.append(here)
            else:
                here = here[curr_key]
                if type(here) == dict:
                    if curr_key not in here_out:
                        here_out[curr_key] = {}
                    here_out = here_out[curr_key]
                elif type(here) == list:
                    if curr_key not in here_out:
                        here_out[curr_key] = []
                    here_out = here_out[curr_key]
                else:
                    here_out[curr_key] = here

    return out_payload


def exclude_paths(payload: Dict, process_list: List[str]) -> Dict:
    """
    Removes the paths in the payload that are excluded.

    Parameters:
            payload (Dict): The input payload object.
            process_list (List[str]): A list of the paths in the input payload that
                                      need to be removed.

    Returns:
            out_payload (Dict): A dictionary object that contains just the paths
                                that are excluded.
    """

    exc_payload = deepcopy(payload)

    for i in range(len(process_list)):
        here = exc_payload
        key_string = process_list[i]
        keys = key_string.split(".")

        # For every key *before* the last one, we concentrate on navigating
        # through the dictionary.
        for i in range(len(keys[:-1])):
            key = keys[i]
            if key.isnumeric() is True:
                here = here[int(key)]
            else:
                # Find here[key]. Update 'here' pointer.
                if key in here:
                    here = here[key]
                else:
                    pass

        here.pop(keys[-1], None)

    return exc_payload


def transform_payload(payload: Dict, includes: List[str], excludes: List[str]) -> Dict:
    """
    Master function that transforms an input payload based on paths specified in
    includes and excludes lists.

    Parameters:
            payload (Dict): The input payload object.
            includes (List[str]): A list of path expressions in dot notation that
                                  need to be included.
            excludes (list[str]): A list of path expressions in dot notation that
                                  need to be excluded.

    Returns:
            out_payload (Dict): The resulting payload object after applying includes
                                and excludes filters.
    """

    # Raise ValueError if includes and/or excludes lists contains an integer list index
    # or if the same path is in includes and excludes lists

    for i in includes:
        index_indices = [m.start() for m in re.finditer(r"\[\d+\]", i)]
        quote_indices = [m.start() for m in re.finditer(r"\"", i)]
        # If an integer index is outside the quotes (if any), return a ValueError
        if len(quote_indices) > 0:
            for ind in index_indices:
                if ind < quote_indices[0] or ind > quote_indices[1]:
                    raise ValueError(
                        "The includes list cannot contain integer list indices."
                    )
        else:
            if len(index_indices) > 0:
                raise ValueError(
                    "The includes list cannot contain integer list indices."
                )
        if i in excludes:
            raise ValueError(
                "The same path cannot be used in both includes and excludes lists."
            )

    for e in excludes:
        index_indices = [m.start() for m in re.finditer(r"\[\d+\]", e)]
        quote_indices = [m.start() for m in re.finditer(r"\"", i)]
        # If an integer index is outside the quotes (if any), return a ValueError
        if len(quote_indices) > 0:
            for ind in index_indices:
                if ind < quote_indices[0] or ind > quote_indices[1]:
                    raise ValueError(
                        "The excludes list cannot contain integer list indices."
                    )
        else:
            if len(index_indices) > 0:
                raise ValueError(
                    "The excludes list cannot contain integer list indices."
                )

    # This is an formatted list of all paths in the payload (using dot notation)
    path_list = [path for path, node in traverse(payload)]

    for i in range(len(path_list)):
        path_list[i] = ".".join(map(str, path_list[i]))

    for i in includes:
        for e in excludes:
            if e in i:
                excludes.remove(e)

    inc_list = filter_path_list(includes, path_list)
    exc_list = filter_path_list(excludes, path_list)
    mod_inp_payload = include_paths(payload, inc_list)
    mod_exc_payload = exclude_paths(mod_inp_payload, exc_list)
    return mod_exc_payload
