from __future__ import annotations

# Manual EURING code table.
TABLE = [
    {
        "code": "-",
        "description": (
            "(one ‘hyphen’) not applicable, because there was no catching at all (for example ‘found’ or ‘found "
            "dead’ or ‘shot’). Field sightings of colour-marked birds or metal rings should be coded with the "
            "hyphen but given Circumstances code 28 or 80 – 89."
        ),
    },
    {"code": "A", "description": "Actively triggered trap (by ringer)."},
    {"code": "B", "description": "trap automatically triggered by Bird."},
    {"code": "C", "description": "Cannon net or rocket net."},
    {"code": "D", "description": "Dazzling."},
    {"code": "F", "description": "Caught in Flight by anything other than a static mist net (e.g. flicked)."},
    {
        "code": "G",
        "description": "Nets put just under the water’s surface and lifted up as waterfowl (ducks, Grebes, divers) swim over it.",
    },
    {"code": "H", "description": "By Hand (with or without hook, noose etc.)."},
    {"code": "L", "description": "Clap net."},
    {"code": "M", "description": "Mist net."},
    {
        "code": "N",
        "description": "On Nest (any method). Not applicable to nestlings which are still in the nest. Use – for these.",
    },
    {"code": "O", "description": "Any Other system (the alphabetic character O)."},
    {"code": "P", "description": "Phut net."},
    {"code": "R", "description": "Round up whilst flightless."},
    {"code": "S", "description": "Bal-chatri or other Snare device."},
    {"code": "T", "description": "Helgoland Trap or duck decoy."},
    {"code": "U", "description": "Dutch net for PlUvialis apricaria."},
    {"code": "V", "description": "Roosting in cavity."},
    {"code": "W", "description": "Passive Walk-in / maze trap."},
    {"code": "Z", "description": "Unknown."},
]
