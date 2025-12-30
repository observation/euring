from __future__ import annotations

# Manual EURING code table.
TABLE = [
    {"code": "0", "description": "Condition completely unknown."},
    {"code": "1", "description": "Dead but no information on how recently the bird had died (or been killed)."},
    {"code": "2", "description": "Freshly dead - within about a week."},
    {
        "code": "3",
        "description": "Not freshly dead - information available that it had been dead for more than about a week.",
    },
    {"code": "4", "description": "Found sick, wounded, unhealthy etc. and known to have been released."},
    {"code": "5", "description": "Found sick, wounded, unhealthy etc. and not released or not known if released."},
    {"code": "6", "description": "Alive and probably healthy but taken into captivity."},
    {"code": "7", "description": "Alive and probably healthy and certainly released."},
    {"code": "8", "description": "Alive and probably healthy and released by a ringer."},
    {"code": "9", "description": "Alive and probably healthy but ultimate fate of bird is not known."},
]
