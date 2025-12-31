from __future__ import annotations

# Manual EURING code table.
TABLE = [
    {"code": "0", "description": "Accurate to the given co-ordinates (radius 1 km).", "category": "numeric"},
    {"code": "1", "description": "Somewhere in a circle with radius 5 km.", "category": "numeric"},
    {"code": "2", "description": "Somewhere in a circle with radius 10 km.", "category": "numeric"},
    {"code": "3", "description": "Somewhere in a circle with radius 20 km.", "category": "numeric"},
    {"code": "4", "description": "Somewhere in a circle with radius 50 km.", "category": "numeric"},
    {"code": "5", "description": "Somewhere in a circle with radius 100 km.", "category": "numeric"},
    {"code": "6", "description": "Somewhere in a circle with radius 500 km.", "category": "numeric"},
    {"code": "7", "description": "Somewhere in a circle with radius 1,000 km.", "category": "numeric"},
    {"code": "8", "description": "Reserved.", "category": "numeric"},
    {
        "code": "9",
        "description": "Somewhere in the country or region given in the field Place Code.",
        "category": "numeric",
    },
    {"code": "A", "description": "Somewhere in a circle with radius 1 m.", "category": "alphabetic"},
    {"code": "B", "description": "Somewhere in a circle with radius 5 m.", "category": "alphabetic"},
    {"code": "C", "description": "Somewhere in a circle with radius 10 m.", "category": "alphabetic"},
    {"code": "D", "description": "Somewhere in a circle with radius 50 m.", "category": "alphabetic"},
    {"code": "E", "description": "Somewhere in a circle with radius 100 m.", "category": "alphabetic"},
    {"code": "F", "description": "Somewhere in a circle with radius 500 m.", "category": "alphabetic"},
    {"code": "G", "description": "Somewhere in a circle with radius 1 km.", "category": "alphabetic"},
    {"code": "H", "description": "Somewhere in a circle with radius 5 km.", "category": "alphabetic"},
    {"code": "I", "description": "Somewhere in a circle with radius 10 km.", "category": "alphabetic"},
    {"code": "J", "description": "Somewhere in a circle with radius 50 km.", "category": "alphabetic"},
    {"code": "K", "description": "Somewhere in a circle with radius 100 km.", "category": "alphabetic"},
    {"code": "L", "description": "Somewhere in a circle with radius 500 km.", "category": "alphabetic"},
    {"code": "M", "description": "Somewhere in a circle with radius 1,000 km.", "category": "alphabetic"},
    {
        "code": "Z",
        "description": "Somewhere in the country or region given in the field Place Code.",
        "category": "alphabetic",
    },
]
