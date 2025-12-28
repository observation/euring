from __future__ import annotations

# Manual EURING code table.
TABLE = {
    "first_character": [
        {"code": "B", "description": "Coloured or numbered leg-ring(s) or flags.", "temporary": False},
        {"code": "C", "description": "Coloured or numbered neck-ring(s).", "temporary": False},
        {"code": "D", "description": "Coloured or numbered wing tag(s).", "temporary": False},
        {"code": "E", "description": "Radio-tracking device.", "temporary": False},
        {"code": "F", "description": "Satellite-tracking device.", "temporary": False},
        {"code": "G", "description": "Transponder.", "temporary": False},
        {"code": "H", "description": "Nasal mark(s).", "temporary": False},
        {"code": "K", "description": "GPS logger.", "temporary": False},
        {"code": "L", "description": "Geolocator logger (recording daylight).", "temporary": False},
        {"code": "R", "description": "Flight feathers stamped with the ring number.", "temporary": True},
        {"code": "S", "description": "Tape on the ring.", "temporary": True},
        {"code": "T", "description": "Dye mark (some part of plumage dyed, painted or bleached).", "temporary": True},
    ],
    "second_character": [
        {"code": "B", "description": "Mark added."},
        {"code": "C", "description": "Mark already present."},
        {"code": "D", "description": "Mark removed."},
        {"code": "E", "description": "Mark changed."},
    ],
    "special_cases": [
        {"code": "MM", "description": "More than one mark present."},
        {"code": "OM", "description": "Other mark(s) present."},
        {"code": "OP", "description": "Other permanent mark(s) present."},
        {"code": "OT", "description": "Other temporary mark(s) present."},
        {"code": "ZZ", "description": "No other marks present or not known to be present."},
    ],
}
