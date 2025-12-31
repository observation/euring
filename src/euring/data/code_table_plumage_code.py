from __future__ import annotations

# Manual EURING code table.
TABLE = [
    {"code": "U", "description": "Unknown or not recorded.", "category": "all_species"},
    {"code": "A", "description": "Adult plumage (if no other codes applicable).", "category": "all_species"},
    {
        "code": "B",
        "description": "Breeding plumage (where species have a distinct breeding plumage).",
        "category": "all_species",
    },
    {"code": "D", "description": "Downy (for nestlings and nidifugous chicks).", "category": "all_species"},
    {"code": "E", "description": "Eclipse plumage (ducks).", "category": "all_species"},
    {
        "code": "F",
        "description": "First winter (typically corresponding to EURING age codes 3 or 5).",
        "category": "all_species",
    },
    {"code": "I", "description": "Immature (except for first winter plumage).", "category": "all_species"},
    {"code": "J", "description": "Juvenile.", "category": "all_species"},
    {
        "code": "W",
        "description": "Winter plumage (where species have a distinct winter plumage).",
        "category": "all_species",
    },
    {"code": "1", "description": "Full winter plumage.", "category": "waders_only"},
    {"code": "2", "description": "Trace of summer plumage.", "category": "waders_only"},
    {"code": "3", "description": "1/4 summer plumage.", "category": "waders_only"},
    {"code": "4", "description": "1/2 summer plumage.", "category": "waders_only"},
    {"code": "5", "description": "3/4 summer plumage.", "category": "waders_only"},
    {"code": "6", "description": "Trace of winter plumage.", "category": "waders_only"},
    {"code": "7", "description": "Full summer plumage.", "category": "waders_only"},
]
