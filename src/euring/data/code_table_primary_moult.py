from __future__ import annotations

# Manual EURING code table (per-character codes for Primary Moult).
TABLE = [
    {"code": "0", "description": "Old feather present."},
    {"code": "1", "description": "Old feather missing or new feather still completely in pin."},
    {"code": "2", "description": "New feather emerging from quill up to one-third grown."},
    {"code": "3", "description": "New feather between one and two thirds grown."},
    {
        "code": "4",
        "description": "More than two thirds grown but waxy sheath still present at base of quills.",
    },
    {"code": "5", "description": "Feather completely new, no waxy sheath remains visible."},
    {"code": "V", "description": "Feather very old (from a generation previous to feathers being moulted)."},
    {"code": "X", "description": "Feather not present on the species (e.g. outermost primary on most finches)."},
]
