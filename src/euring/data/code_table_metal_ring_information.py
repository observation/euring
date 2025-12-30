from __future__ import annotations

# Manual EURING code table.
TABLE = [
    {"code": 0, "description": "Metal ring is not present."},
    {
        "code": 1,
        "description": "Metal ring added (where no metal ring was present), position (on tarsus or above) unknown or "
        "unrecorded.",
    },
    {"code": 2, "description": "Metal ring added (where no metal ring was present), definitely on tarsus."},
    {"code": 3, "description": "Metal ring added (where no metal ring was present), definitely above tarsus."},
    {"code": 4, "description": "Metal ring is already present."},
    {"code": 5, "description": "Metal ring changed."},
    {"code": 6, "description": "Metal ring removed and bird released alive (use code 4 if bird was dead)."},
    {
        "code": 7,
        "description": "Metal ring added, where a metal ring was already present. N.b. within EURING there is an explicit "
        "agreement that ringers must not add a metal ring when one is already present (except in "
        "circumstances where the existing ring needs to be replaced because of wear).",
    },
    {
        "code": 9,
        "description": "No information provided (e.g., colour ring read without metal ring information, or colour ring found without the bird).",
    },
]
