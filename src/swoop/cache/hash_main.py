import base64
from copy import deepcopy
import hashlib
import re
from typing import Dict, List, Union


def sha1(*args: List[str]) -> str:
    """
    Hashes the values in the transformed payload using the SHA1 algorithm.

    Parameters:
            args (List[str]): An input dictionary object that will be hashed
                              using the SHA1 algorithm.

    Returns:
            hashed (str): A base-64 encoded hash of the input dictionary object.
    """
    sha = hashlib.sha1()
    for arg in args:
        sha.update(str(arg).encode())
    hashed = base64.b64encode(sha.digest())
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
            for k, v in traverse(v, path + [k]):
                yield k, v


def order_dict(payload: Dict) -> Dict:
    """
    Reorders the keys in the payload object alphabetically.

    Parameters:
            payload (Dict): The input payload whose keys will be ordered
                            alphabetically.

    Returns:
            result (Dict): The input payload with keys (including nested)
                           ordered alphabetically.
    """
    result = {}
    for k, v in sorted(payload.items()):
        if isinstance(v, dict):
            result[k] = order_dict(v)
        elif isinstance(v, list):
            result[k] = []
            for i in range(len(v)):
                elem = v[i]
                if isinstance(elem, dict):
                    result[k].append(order_dict(elem))
                else:
                    result[k].append(elem)
        else:
            result[k] = v

    return result


def eval_to_list(expressions: List[str], path_list: List[str]) -> List[str]:
    """
    Finds the paths in the path list that match the expressions in
    either the includes or excludes lists using regex.

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
        regex = ""
        split_exp = exp.split(".")
        for e in split_exp:
            if "[" in e:
                sub = e.split("[")
                if "[*]" in e:
                    regex += sub[0] + ".[0-9]."
                else:
                    regex += sub[0] + ".[" + sub[1] + "."
            elif e == "*":
                regex += ".[-a-z0-9]."
            else:
                regex += e + "."
        regex = regex.strip(".")
        r = re.compile(regex)

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

    # Sort entire payload alphabetically (all keys)

    payload = order_dict(payload)

    # This is an formatted list of all paths in the payload (using dot notation)
    path_list = [path for path, node in traverse(payload)]

    for i in range(len(path_list)):
        path_list[i] = ".".join(map(str, path_list[i]))

    # Check if same path is in both lists

    for i in includes:
        if i in excludes:
            raise Exception(
                "The same path cannot be used in both includes and excludes lists."
            )

    if excludes == ["*"]:
        inc_list = eval_to_list(includes, path_list)
        mod_inp_payload = include_paths(payload, inc_list)
        return mod_inp_payload
    else:
        if includes == [
            "process.workflow",
            "features[*].id",
            "features[*].collection",
            "*",
        ]:
            exc_list = eval_to_list(excludes, path_list)
            mod_exc_payload = exclude_paths(payload, exc_list)
            return mod_exc_payload
        else:
            for i in includes:
                for e in excludes:
                    if i in e:
                        pass
                    if e in i:
                        excludes.remove(e)

            inc_list = eval_to_list(includes, path_list)
            exc_list = eval_to_list(excludes, path_list)
            mod_inp_payload = include_paths(payload, inc_list)
            mod_exc_payload = exclude_paths(mod_inp_payload, exc_list)
            return mod_exc_payload
