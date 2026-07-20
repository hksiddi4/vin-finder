colors_dict_hummer_ev = {
    "GAZ": "INTERSTELLAR WHITE",
    "GBA": "VOID BLACK",
    "GNO": "METEORITE METALLIC",
    "GXN": "DEEP AURORA METALLIC",
    "GC5": "AFTERBURNER TINTCOAT",
    "G7X": "TIDE METALLIC",
    "GKK": "SUPERNOVA METALLIC",
    "GLG": "NEPTUNE BLUE MATTE",
    "GAG": "SOLAR ORANGE",
    "GAI": "GRAPHITE BLUE METALLIC",
    "G7W": "MOONSHOT GREEN MATTE",
    "G42": "COASTAL DUNE",
    "GBL": "MAGNUS GRAY MATTE",
    "GNR": "AUBURN MATTE",
}

trim_dict_hummer_ev = {
    "1SE": "2", # SUV
    "1SF": "2X", # SUV
    "1SG": "3X", # SUV
    "1SB": "2", # Pickup
    "1SC": "2X", # Pickup
    "1SD": "3X", # Pickup
    "3VL": "2X", # 
    "FH1": "EDITION 1", # 2022 & 2024 only
}

mmc = {
    "TT35743": "HUMMER EV PICKUP",
    "TT35526": "HUMMER EV SUV"
}

# variables/hummer_ev.py

urlIdent_2022_hummer_ev = {
    "1GT1": ["0FDA"], 
    "1GT4": ["0FDA"] 
}

urlIdent_2023_hummer_ev = { 
    "1GT1": ["0FDA", "0DDA", "0DDB"], # Edition 1 & 3X Pickup
    "1GT4": ["0FDA", "0DDA", "0DDB"] 
}

urlIdent_2024_hummer_ev = {
    "1GKB": ["0NDE", "0RDC", "0SDC", "0FDA"], # SUV trims (0FDA = Edition 1 SUV here)
    "1GT4": ["0BDD", "0DDA"],                 # Pickup trims
    "1GT1": ["0BDD", "0DDA"]
}

urlIdent_2025_hummer_ev = {
    "1GKT": ["0NDE", "0RDC"],         # 2X & 3X SUV (Newer 2025 prefix)
    "1GKB": ["0NDE", "0RDC"],         # 2X & 3X SUV (Legacy 2025 prefix)
    "1GT4": ["0BDD", "0DDA", "0DDB"], # 2X & 3X Pickup (Standard)
    "1GT1": ["0BDD", "0DDA", "0DDB"]  # 2X & 3X Pickup (Specialized / Heavy Duty)
}

urlIdent_2026_hummer_ev = {
    # SUV Trims (2X: EHDE, ENDE | 3X: ESDC, ERDC)
    "1GKT": ["EHDE", "ENDE", "ESDC", "ERDC"], # New 2026 primary SUV prefix
    # Pickup Trims (2X: EADD, EBDD | 3X: EDDA, EDDB)
    "1GT4": ["EADD", "EBDD", "EDDA", "EDDB"], # Primary Pickup prefix
    "1GT1": ["EDDA", "EDDB"]                  # Specialized/HD Pickup prefix
}
