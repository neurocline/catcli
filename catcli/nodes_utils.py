"""
author: deadc0de6 (https://github.com/deadc0de6)
Copyright (c) 2024, deadc0de6

nodes helpers
"""

import os

# local imports
from catcli import nodes


def path_to_top(path: str) -> str:
    """path pivot under top"""
    pre = f"/{nodes.NAME_TOP}"
    if not path.startswith(pre):
        # prepend with top node path
        path = pre + path
    return path


def path_to_search_all(path: str) -> str:
    """path to search for all subs"""
    if not path:
        path = "/"
    if not path.startswith("/"):
        path = "/" + path
    pre = f"/{nodes.NAME_TOP}"
    if not path.startswith(pre):
        # prepend with top node path
        path = pre + path
    # if not path.endswith("/"):
    #     # ensure ends with a separator
    #     path += "/"
    # if not path.endswith(WILD):
    #     # add wild card
    #     path += WILD
    return path
