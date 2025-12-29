from __future__ import annotations

# Generated from curated EURING reference data.
TABLE = [
    {
        "code": "00",
        "description": "Found (letter reports 'found'); no mention of the bird or its body in recovery report.",
        "name": "Found",
        "updated": "2008-05-06",
    },
    {
        "code": "01",
        "description": "Found; bird or body mentioned in recovery letter.",
        "name": "Bird found",
        "updated": "2008-05-06",
    },
    {
        "code": "02",
        "description": "Ring only found in circumstances where it is unclear if the ring had been moved since the bird "
        "died.  If ring had been moved (eg found at Post Office, in chest of drawers), then this should be "
        "coded in column 31 (moved before capture/recapture/recovery)",
        "name": "Ring only found",
        "updated": "2008-11-05",
    },
    {
        "code": "03",
        "description": "Ring and leg only found in natural circumstances.",
        "name": "Leg & ring only found",
        "updated": "2008-11-05",
    },
    {"code": "04", "description": "Code 04 is not used.", "name": "Not defined", "updated": "2008-05-06"},
    {"code": "05", "description": "Code 05 is not used.", "name": "Not defined", "updated": "2008-05-06"},
    {
        "code": "06",
        "description": "Found on ship unless there is further indication that the bird was caught in fishing gear, hit "
        "wires, attracted to lights etc.",
        "name": "Found on ship",
        "updated": "2008-05-06",
    },
    {
        "code": "07",
        "description": "Joined or attracted to domestic livestock (but not if the bird was shot or trapped to protect the "
        "animals to which it has been attracted).",
        "name": "Attracted to domestic animals",
        "updated": "2008-05-06",
    },
    {
        "code": "08",
        "description": "Dead or seriously harmed by ringer through catching or handling processes.",
        "name": "Ringing casualty",
        "updated": "2008-05-06",
    },
    {
        "code": "09",
        "description": "Recovery caused by the ring or mark on the bird - including entangled because of the ring or "
        "injuries caused by the ring.",
        "name": "Ring caused recovery",
        "updated": "2008-05-06",
    },
    {
        "code": "10",
        "description": "Shot - for reasons other than codes 12 - 16.",
        "name": "Shot",
        "updated": "2008-05-06",
    },
    {"code": "11", "description": "Found shot.", "name": "Found shot", "updated": "2008-05-06"},
    {
        "code": "12",
        "description": "Shot to protect crops, foodstuffs, animals or game species.",
        "name": "Crop protection - shot",
        "updated": "2008-05-06",
    },
    {
        "code": "13",
        "description": "Shot in the course of nature protection procedures (eg gulls culled to protect young terns, gulls "
        "culled to provide nesting habitat for other species).",
        "name": "Nature conservation - shot",
        "updated": "2008-11-05",
    },
    {
        "code": "14",
        "description": "Shot to protect human life  e.g. airstrike prevention, human health (roosts on buildings or on "
        "drinking water reservoirs).",
        "name": "Public safety - shot",
        "updated": "2008-05-06",
    },
    {
        "code": "15",
        "description": "Shot to provide plumage for decoration or commerce (taxidermy; fishing lures etc.) OR shot as part "
        "of a scientific investigation (but NOT because the bird was ringed).",
        "name": "Shot for plumage/skin/science",
        "updated": "2008-11-05",
    },
    {
        "code": "16",
        "description": "Shot because it was ringed or marked.",
        "name": "Shot because of ring",
        "updated": "2008-05-06",
    },
    {"code": "17", "description": "Code 17 is not used.", "name": "Not defined", "updated": "2008-05-06"},
    {"code": "18", "description": "Code 18 is not used.", "name": "Not defined", "updated": "2008-05-06"},
    {
        "code": "19",
        "description": "Capturado, tué, chassé, tué à la chasse etc.  words or phrases used to indicate the bird has been "
        "hunted has probably been shot.",
        "name": "Hunted",
        "updated": "2008-11-05",
    },
    {
        "code": "20",
        "description": "Hunted, trapped (including all captures by ringers), poisoned intentionally by man but not shot and "
        "not for reasons using codes 21 - 29.",
        "name": "Intentionally taken",
        "updated": "2008-11-03",
    },
    {
        "code": "21",
        "description": "Trapped for caging. Use with condition code to indicate birds found in captivity and column 31 moved "
        "before capture/recapture/recovery for birds not found where they were caught. NB: birds taken into "
        "captivity for treatment are not included here.",
        "name": "Caged",
        "updated": "2008-11-05",
    },
    {
        "code": "22",
        "description": "Trapped, poisoned etc. to protect crops, foodstuffs, animals or game species. Not shot - compare "
        "with code 12.",
        "name": "Crop protection",
        "updated": "2008-05-06",
    },
    {
        "code": "23",
        "description": "Trapped, poisoned etc. during nature protection procedures. Not shot - compare with code13.",
        "name": "Nature conservation",
        "updated": "2008-05-06",
    },
    {
        "code": "24",
        "description": "Trapped, poisoned etc. to protect human life. Not shot - compare with code 14.",
        "name": "Public safety",
        "updated": "2008-05-06",
    },
    {
        "code": "25",
        "description": "Trapped, poisoned etc. for plumage or during scientific investigation. Not shot - compare with code "
        "15.",
        "name": "Scientific investigation",
        "updated": "2008-05-06",
    },
    {
        "code": "26",
        "description": "Trapped, poisoned etc. because it was ringed. Not shot - compare with code 16.",
        "name": "Taken because of ring",
        "updated": "2008-05-06",
    },
    {
        "code": "27",
        "description": "Found at or in nestbox or other structure specially placed or modified by man for birds to use. "
        "Compare with code 46.",
        "name": "At nestbox/artificial site",
        "updated": "2008-05-06",
    },
    {
        "code": "28",
        "description": "Ring number of metal ring read in field without the bird being caught.",
        "name": "Metal ring read in field",
        "updated": "2008-05-06",
    },
    {
        "code": "29",
        "description": "Use codes 80 - 89 if more information is available about the type of colour mark.",
        "name": "Colour mark record",
        "updated": "2008-05-06",
    },
    {"code": "30", "description": "Oil.", "name": "Oil victim", "updated": "2008-05-06"},
    {
        "code": "31",
        "description": "Contact with discarded human materials (old tins, discarded fishing line, metal swarf, plastic, "
        "sticky substances but not oil).",
        "name": "Discarded human materials",
        "updated": "2008-05-06",
    },
    {
        "code": "32",
        "description": "Contact with human artefacts which are still in use and NOT intended as protection against birds or "
        "set to trap birds or other animals  e.g. tangled in barbed wire; caught in sports netting; caught in "
        "fishnets hanging to dry on the shore.",
        "name": "Human artefact",
        "updated": "2008-05-06",
    },
    {
        "code": "33",
        "description": "Entangled in crop protection nets(including fruit netting, nets over stored food or fishponds). "
        "Includes threads or fibres not made into nets, but used for crop protection.",
        "name": "Nets to protect crops",
        "updated": "2008-11-05",
    },
    {
        "code": "34",
        "description": "Accidentally trapped where the intention was to trap other species of birds or vertebrates (eg "
        "Erithacus rubecula in trap for Pyrrhula pyrrhula in an orchard, a bird caught in a mouse trap, or in "
        "fish nets or on a fist hook WHILE the nets or hook were bei",
        "name": "Trap set for other species",
        "updated": "2008-11-05",
    },
    {
        "code": "35",
        "description": "Electrocuted. This overrides codes for Hit wires (43) or Entered building (46) if electrocution "
        "appears the major cause of death.",
        "name": "Electrocuted",
        "updated": "2008-05-06",
    },
    {"code": "36", "description": "Radioactivity.", "name": "Radioactivity", "updated": "2008-05-06"},
    {
        "code": "37",
        "description": "Poisoned through chemical pollution. Chemical(s) identified. Use codes 20 - 26 or 34 if poisoning "
        "was deliberate.",
        "name": "Poisoned: poison identified",
        "updated": "2008-05-06",
    },
    {
        "code": "38",
        "description": "Poisoned through chemical pollution but identity of chemical agent (agents) not known.",
        "name": "Poisoned: poison not identified",
        "updated": "2008-05-06",
    },
    {"code": "39", "description": "Code 39 is not used.", "name": "Not defined", "updated": "2008-05-06"},
    {
        "code": "40",
        "description": "Road  used with circumstances presumed (col 80): 0 definitely through impact with road vehicle; 1 "
        "dead on road, presumed impact with road vehicle; OR with moved before capture/recapture/recovery "
        "(col 31) 2 moved by vehicle from point of impact",
        "name": "Road casualty",
        "updated": "2008-11-05",
    },
    {
        "code": "41",
        "description": "Railway - used with fields circumstances presumed and moved before capture/recapture/recovery as for "
        "code 40.",
        "name": "Railway casualty",
        "updated": "2008-11-05",
    },
    {
        "code": "42",
        "description": "Aircraft - used with used with fields circumstances presumed and moved before "
        "capture/recapture/recovery as for code 40.  Take care whether impact with aircraft or ground vehicle "
        "is cause of recovery on airfields.",
        "name": "Aircraft casualty",
        "updated": "2008-11-05",
    },
    {
        "code": "43",
        "description": "Collision with (or presumed) THIN manmade structure  wires, masts, cables, ship's rigging, aerials "
        "etc.  See code 45 for THICK man-made structures. See code 91 for wind turbines.",
        "name": "Hit wires",
        "updated": "2012-01-30",
    },
    {
        "code": "44",
        "description": "Collision with (or presumed) glass or other transparent materials  windows, windbreaks, windows of "
        "static vehicles. See code 91 for wind turbines.",
        "name": "Hit glass",
        "updated": "2012-01-30",
    },
    {
        "code": "45",
        "description": "Collision with (or presumed) THICK manmade structure - building, bridge, etc. See 91 for wind "
        "turbines.",
        "name": "Hit man-made structure",
        "updated": "2012-01-30",
    },
    {
        "code": "46",
        "description": "Entered manmade structure NOT built or modified to trap animals (code 34) or as a nestbox (code 27)  "
        "building, letterbox, etc.  See field status for codes for roosting, breeding etc.",
        "name": "Entered building",
        "updated": "2008-11-05",
    },
    {
        "code": "47",
        "description": "Attracted to lights (not being used as a deliberate trapping method)  often associated with foggy "
        "weather.  NB: P or S in status indicates at a lighthouse or lightship.",
        "name": "Dazzled by lights",
        "updated": "2008-11-05",
    },
    {
        "code": "48",
        "description": "Recovered as a result of active human occupation not covered by other codes - industrial, "
        "agricultural, forestry, sporting, military.  See manual for examples.",
        "name": "Active human enterprise",
        "updated": "2008-11-05",
    },
    {
        "code": "49",
        "description": "Drowned in artificial water container: water butt, forestry fire tank etc. where the edges of the "
        "water surface are artificial and may trap any bird in the water (NB: category 70 would apply to a "
        "garden pond).",
        "name": "Artificial water container",
        "updated": "2008-05-06",
    },
    {
        "code": "50",
        "description": "Contusions, breaks, general trauma where no other cause given.",
        "name": "Injured",
        "updated": "2008-05-06",
    },
    {
        "code": "51",
        "description": "Malformations - congenital, mechanical (e.g. from broken bill) or from tumours.",
        "name": "Malformation",
        "updated": "2008-05-06",
    },
    {
        "code": "52",
        "description": "Fungal infections (e.g. aspergillosis etc.).",
        "name": "Fungal infection",
        "updated": "2008-05-06",
    },
    {"code": "53", "description": "Viral infections.", "name": "Viral infection", "updated": "2008-05-06"},
    {
        "code": "54",
        "description": "Bacterial infections (but use code 56 for Botulism).",
        "name": "Bacterial infection",
        "updated": "2008-05-06",
    },
    {
        "code": "55",
        "description": "Other endoparasites (e.g. bloodparasites, nematodes, trematodes etc.).",
        "name": "Endoparasites",
        "updated": "2008-05-06",
    },
    {"code": "56", "description": "Botulism.", "name": "Botulism", "updated": "2008-05-06"},
    {"code": "57", "description": "Redtide (dinoflagellate poisoning).", "name": "Red Tide", "updated": "2008-05-06"},
    {
        "code": "58",
        "description": "Combination of any of the above without definite single cause being known.",
        "name": "Sick",
        "updated": "2008-05-06",
    },
    {
        "code": "59",
        "description": "Veterinary examination made and report available  no positive conclusions.",
        "name": "Veterinary report available",
        "updated": "2008-05-06",
    },
    {
        "code": "60",
        "description": "Taken by unspecified animal (but use code 20 if taken by falconer's trained bird).",
        "name": "Taken by animal",
        "updated": "2008-05-06",
    },
    {"code": "61", "description": "Taken by cat.", "name": "Taken by cat", "updated": "2008-05-06"},
    {
        "code": "62",
        "description": "Taken by other domestic animal or one in captivity (e.g. farmed mink or zoo animals, includes "
        "poultry, reptiles etc. in captivity) but use code 20 if taken by falconer's trained bird.",
        "name": "Taken by domestic animal",
        "updated": "2008-05-06",
    },
    {
        "code": "63",
        "description": "Taken by wild or feral mammal (include escaped mink).",
        "name": "Taken by wild mammal",
        "updated": "2008-05-06",
    },
    {
        "code": "64",
        "description": "Taken by owl or raptor  exact identification of predator available (but use code 20 if taken by "
        "falconer's trained bird).",
        "name": "Taken by owl or raptor",
        "updated": "2008-11-05",
    },
    {
        "code": "65",
        "description": "Taken by owl or raptor  exact identification of predator not known.",
        "name": "Taken by predatory bird",
        "updated": "2008-05-06",
    },
    {
        "code": "66",
        "description": "Taken by other species of bird (not conspecific).",
        "name": "Taken by bird",
        "updated": "2008-05-06",
    },
    {"code": "67", "description": "Taken by conspecific.", "name": "Taken by a conspecific", "updated": "2008-05-06"},
    {
        "code": "68",
        "description": "Taken by reptile, amphibian or fish.",
        "name": "Taken by reptile, amphibian or fish",
        "updated": "2008-05-06",
    },
    {
        "code": "69",
        "description": "Taken by invertebrate (e.g. wasps, ants, bees, spider etc).",
        "name": "Taken by other animals",
        "updated": "2008-05-06",
    },
    {
        "code": "70",
        "description": "Drowned  but use code 49 if drowned in an artificial water container.  Note also moved before "
        "capture/recapture/recovery (col 31).",
        "name": "Drowned",
        "updated": "2008-11-05",
    },
    {
        "code": "71",
        "description": "Tangled in natural object (e.g. tree, sheep's wool etc.). NB: tangling by ring or mark is coded 09.",
        "name": "Tangled in natural object",
        "updated": "2008-05-06",
    },
    {
        "code": "72",
        "description": "In natural hole or cave.  NB: status (breeding, roosting etc) coded in col 38.",
        "name": "In natural hole",
        "updated": "2008-11-05",
    },
    {
        "code": "73",
        "description": "Collided with any sort of natural object (e.g. tree, cliff etc.). If collision during violent storm "
        "etc. use code 78.",
        "name": "Collision with natural object",
        "updated": "2008-05-06",
    },
    {
        "code": "74",
        "description": "Poor condition with indication that cold weather was cause.",
        "name": "Cold weather",
        "updated": "2008-05-06",
    },
    {
        "code": "75",
        "description": "Poor condition with indication that hot weather was cause.",
        "name": "Hot weather",
        "updated": "2008-05-06",
    },
    {
        "code": "76",
        "description": "Poor condition.  Starvation or thirst may be mentioned but no indication of cause leading to poor "
        "condition of the bird.",
        "name": "Poor condition",
        "updated": "2008-05-06",
    },
    {"code": "77", "description": "Caught in ice.", "name": "Iced in", "updated": "2008-05-06"},
    {
        "code": "78",
        "description": "Violent climatological phenomena were involved in the recovery  strong winds, tempests, hail, "
        "whirlwind, floods etc.",
        "name": "Violent weather",
        "updated": "2008-05-06",
    },
    {"code": "79", "description": "Code 79 is not used.", "name": "Not defined", "updated": "2008-05-06"},
    {
        "code": "80",
        "description": "Bird identified as an individual in the field by something other than the metal ring.",
        "name": "Identified by other means",
        "updated": "2008-05-06",
    },
    {
        "code": "81",
        "description": "Bird identified from coloured or numbered leg ring(s).",
        "name": "Identified from leg ring(s)",
        "updated": "2008-05-06",
    },
    {
        "code": "82",
        "description": "Bird identified from coloured or numbered neck ring(s).",
        "name": "Identified from neck ring(s)",
        "updated": "2008-05-06",
    },
    {
        "code": "83",
        "description": "Bird identified from wing tags.",
        "name": "Identified from wing tags",
        "updated": "2008-05-06",
    },
    {
        "code": "84",
        "description": "Bird identified using radio tracking.",
        "name": "Identified with radio tracking",
        "updated": "2008-05-06",
    },
    {
        "code": "85",
        "description": "Bird identified using satellite tracking.",
        "name": "Identified with satellite tracking",
        "updated": "2008-05-06",
    },
    {
        "code": "86",
        "description": "Bird identified using transponder.",
        "name": "Identified from transponder",
        "updated": "2008-05-06",
    },
    {
        "code": "87",
        "description": "Bird identified from nasal mark(s).",
        "name": "Identified from nasal tags",
        "updated": "2008-05-06",
    },
    {
        "code": "88",
        "description": "Bird identified from flight feather(s) stamped with the ring number.",
        "name": "Identified from flight feathers",
        "updated": "2008-05-06",
    },
    {
        "code": "89",
        "description": "Bird identified from body or wing painting.",
        "name": "Identified from body painting",
        "updated": "2008-05-06",
    },
    {
        "code": "91",
        "description": "Any bird found dead at site of wind turbine. This will include death by striking blades or tower and "
        "any other cause including death by barotrauma.",
        "name": "Found dead at site of wind turbine.",
        "updated": "2012-01-30",
    },
    {
        "code": "99",
        "description": "No information at all (e.g. ring number written on postcard with no mention of the bird, whether "
        "found, whether dead or alive).",
        "name": "Unknown",
        "updated": "2008-05-06",
    },
]

__all__ = ["TABLE"]
