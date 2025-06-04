from __future__ import annotations
import re
from typing import Dict, List

_BLOCK_RX = re.compile(r"\$\s*([A-Z_ ]+?)\s*\$([\s\S]*?)(?=\$\s*[A-Z_ ]+\s*\$|\Z)",
                       flags=re.I)

def _extract_blocks(src):
    return {name.strip().upper(): body.strip() for name, body in _BLOCK_RX.findall(src)}


def _split_subblocks(body, tag):
    rx = rf"{tag}\d+\s*:\s*([\s\S]*?)(?={tag}\d+\s*:|\Z)"
    return re.findall(rx, body, flags=re.I)


def _num_or_eval(expr):
    try:
        return eval(expr, {"__builtins__": {}}, {})
    except Exception:
        return expr

