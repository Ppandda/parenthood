from libs.transform_time import unified_time_to_weeks

# DE1 numeric
DE1 = {
    "plot_type": "continuous",
    "x_label": "Year",
}

# DE2 – single choice
DE2 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Woman",
        2: "Man",
        3: "Non-binary person",
        4: "Prefer not to answer",
    },
}


# DE3 – multiple choice (ethnic origin / ancestry)
DE3 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Western Europe (e.g., Greece, Sweden, United Kingdom)",
        2: "Eastern Europe (e.g., Hungary, Poland, Russia)",
        3: "North Africa (e.g., Egypt, Morocco, Sudan)",
        4: "Sub-Saharan Africa (e.g., Kenya, Nigeria, South Africa)",
        5: "West Asia / Middle East (e.g., Iran, Israel, Saudi Arabia)",
        6: "South and Southeast Asia (e.g., India, Indonesia, Singapore)",
        7: "East and Central Asia (e.g., China, Japan, Uzbekistan)",
        8: "Pacific / Oceania (e.g., Australia, Papua New Guinea, Fiji)",
        9: "North America (Canada, United States)",
        10: "Central America and Caribbean (e.g., Jamaica, Mexico, Panama)",
        11: "South America (e.g., Brazil, Chile, Colombia)",
        12: "Self describe",
        13: "Prefer not to answer",
    },
}


# DE4 – single choice (economic situation during childhood)
DE4 = {
    "plot_type": "categorical",
    "value_map": {
        1: "We struggled to meet basic needs (food, shelter, clothing).",
        2: "We met basic needs but had little extra for other things.",
        3: "We were comfortable and could afford some extras beyond our basic needs.",
        4: "We were well-off and could easily afford many extras and savings.",
        5: "Prefer not to say.",
    },
}


# DE5 – single choice (country lived in during first 18 years)
DE5 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Afghanistan",
        2: "Akrotiri",
        3: "Albania",
        4: "Algeria",
        5: "American Samoa",
        6: "Andorra",
        7: "Angola",
        8: "Anguilla",
        9: "Antarctica",
        10: "Antigua and Barbuda",
        11: "Argentina",
        12: "Armenia",
        13: "Aruba",
        14: "Ashmore and Cartier Islands",
        15: "Australia",
        16: "Austria",
        17: "Azerbaijan",
        18: "Bahamas, The",
        19: "Bahrain",
        20: "Bangladesh",
        21: "Barbados",
        22: "Bassas da India",
        23: "Belarus",
        24: "Belgium",
        25: "Belize",
        26: "Benin",
        27: "Bermuda",
        28: "Bhutan",
        29: "Bolivia",
        30: "Bosnia and Herzegovina",
        31: "Botswana",
        32: "Bouvet Island",
        33: "Brazil",
        34: "British Indian Ocean Territory",
        35: "British Virgin Islands",
        36: "Brunei",
        37: "Bulgaria",
        38: "Burkina Faso",
        39: "Burma",
        40: "Burundi",
        41: "Cambodia",
        42: "Cameroon",
        43: "Canada",
        44: "Cape Verde",
        45: "Cayman Islands",
        46: "Central African Republic",
        47: "Chad",
        48: "Chile",
        49: "China",
        50: "Christmas Island",
        51: "Clipperton Island",
        52: "Cocos (Keeling) Islands",
        53: "Colombia",
        54: "Comoros",
        55: "Congo, Democratic Republic of the",
        56: "Congo, Republic of the",
        57: "Cook Islands",
        58: "Coral Sea Islands",
        59: "Costa Rica",
        60: "Cote d'Ivoire",
        61: "Croatia",
        62: "Cuba",
        63: "Cyprus",
        64: "Czech Republic",
        65: "Denmark",
        66: "Dhekelia",
        67: "Djibouti",
        68: "Dominica",
        69: "Dominican Republic",
        70: "Ecuador",
        71: "Egypt",
        72: "El Salvador",
        73: "Equatorial Guinea",
        74: "Eritrea",
        75: "Estonia",
        76: "Ethiopia",
        77: "Europa Island",
        78: "Falkland Islands (Islas Malvinas)",
        79: "Faroe Islands",
        80: "Fiji",
        81: "Finland",
        82: "France",
        83: "French Guiana",
        84: "French Polynesia",
        85: "French Southern and Antarctic Lands",
        86: "Gabon",
        87: "Gambia, The",
        88: "Gaza Strip",
        89: "Georgia",
        90: "Germany",
        91: "Ghana",
        92: "Gibraltar",
        93: "Glorioso Islands",
        94: "Greece",
        95: "Greenland",
        96: "Grenada",
        97: "Guadeloupe",
        98: "Guam",
        99: "Guatemala",
        100: "Guernsey",
        101: "Guinea",
        102: "Guinea-Bissau",
        103: "Guyana",
        104: "Haiti",
        105: "Heard Island and McDonald Islands",
        106: "Holy See (Vatican City)",
        107: "Honduras",
        108: "Hong Kong",
        109: "Hungary",
        110: "Iceland",
        111: "India",
        112: "Indonesia",
        113: "Iran",
        114: "Iraq",
        115: "Ireland",
        116: "Isle of Man",
        117: "Israel",
        118: "Italy",
        119: "Jamaica",
        120: "Jan Mayen",
        121: "Japan",
        122: "Jersey",
        123: "Jordan",
        124: "Juan de Nova Island",
        125: "Kazakhstan",
        126: "Kenya",
        127: "Kiribati",
        128: "Korea, North",
        129: "Korea, South",
        130: "Kuwait",
        131: "Kyrgyzstan",
        132: "Laos",
        133: "Latvia",
        134: "Lebanon",
        135: "Lesotho",
        136: "Liberia",
        137: "Libya",
        138: "Liechtenstein",
        139: "Lithuania",
        140: "Luxembourg",
        141: "Macau",
        142: "Macedonia",
        143: "Madagascar",
        144: "Malawi",
        145: "Malaysia",
        146: "Maldives",
        147: "Mali",
        148: "Malta",
        149: "Marshall Islands",
        150: "Martinique",
        151: "Mauritania",
        152: "Mauritius",
        153: "Mayotte",
        154: "Mexico",
        155: "Micronesia, Federated States of",
        156: "Moldova",
        157: "Monaco",
        158: "Mongolia",
        159: "Montserrat",
        160: "Morocco",
        161: "Mozambique",
        162: "Namibia",
        163: "Nauru",
        164: "Navassa Island",
        165: "Nepal",
        166: "Netherlands",
        167: "Netherlands Antilles",
        168: "New Caledonia",
        169: "New Zealand",
        170: "Nicaragua",
        171: "Niger",
        172: "Nigeria",
        173: "Niue",
        174: "Norfolk Island",
        175: "Northern Mariana Islands",
        176: "Norway",
        177: "Oman",
        178: "Pakistan",
        179: "Palau",
        180: "Panama",
        181: "Papua New Guinea",
        182: "Paracel Islands",
        183: "Paraguay",
        184: "Peru",
        185: "Philippines",
        186: "Pitcairn Islands",
        187: "Poland",
        188: "Portugal",
        189: "Puerto Rico",
        190: "Qatar",
        191: "Reunion",
        192: "Romania",
        193: "Russia",
        194: "Rwanda",
        195: "Saint Helena",
        196: "Saint Kitts and Nevis",
        197: "Saint Lucia",
        198: "Saint Pierre and Miquelon",
        199: "Saint Vincent and the Grenadines",
        200: "Samoa",
        201: "San Marino",
        202: "Sao Tome and Principe",
        203: "Saudi Arabia",
        204: "Senegal",
        205: "Serbia and Montenegro",
        206: "Seychelles",
        207: "Sierra Leone",
        208: "Singapore",
        209: "Slovakia",
        210: "Slovenia",
        211: "Solomon Islands",
        212: "Somalia",
        213: "South Africa",
        214: "South Georgia and the South Sandwich Islands",
        215: "Spain",
        216: "Spratly Islands",
        217: "Sri Lanka",
        218: "Sudan",
        219: "Suriname",
        220: "Svalbard",
        221: "Swaziland",
        222: "Sweden",
        223: "Switzerland",
        224: "Syria",
        225: "Taiwan",
        226: "Tajikistan",
        227: "Tanzania",
        228: "Thailand",
        229: "Timor-Leste",
        230: "Togo",
        231: "Tokelau",
        232: "Tonga",
        233: "Trinidad and Tobago",
        234: "Tromelin Island",
        235: "Tunisia",
        236: "Turkey",
        237: "Turkmenistan",
        238: "Turks and Caicos Islands",
        239: "Tuvalu",
        240: "Uganda",
        241: "Ukraine",
        242: "United Arab Emirates",
        243: "United Kingdom",
        244: "United States",
        245: "Uruguay",
        246: "Uzbekistan",
        247: "Vanuatu",
        248: "Venezuela",
        249: "Vietnam",
        250: "Virgin Islands",
        251: "Wake Island",
        252: "Wallis and Futuna",
        253: "West Bank",
        254: "Western Sahara",
        255: "Yemen",
        256: "Zambia",
        257: "Zimbabwe",
    },
}


# DE6 – single choice (current country of residence)
DE6 = DE5


# DE7 – multiple choice
DE7 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Single (never married)",
        2: "Living with partner",
        3: "Married",
        4: "Separated",
        5: "Widowed",
        6: "Divorced",
        7: "Prefer not to answer",
    },
}


# DE8 – single choice
DE8 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Postdoc",
        2: "Non-tenure-track faculty",
        3: "Tenure-track faculty",
        4: "Tenured faculty",
        5: "Other (please specify)",
    },
}


# DE9 – multiple choice
DE9 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Albania",
        2: "Andorra",
        3: "Armenia",
        4: "Austria",
        5: "Azerbaijan",
        6: "Belarus",
        7: "Belgium",
        8: "Bosnia and Herzegovina",
        9: "Bulgaria",
        10: "Croatia",
        11: "Cyprus",
        12: "Czech Republic",
        13: "Denmark",
        14: "Estonia",
        15: "Finland",
        16: "France",
        17: "Georgia",
        18: "Germany",
        19: "Greece",
        20: "Hungary",
        21: "Iceland",
        22: "Ireland",
        23: "Italy",
        24: "Kazakhstan",
        25: "Kosovo",
        26: "Latvia",
        27: "Liechtenstein",
        28: "Lithuania",
        29: "Luxembourg",
        30: "Malta",
        31: "Moldova",
        32: "Monaco",
        33: "Montenegro",
        34: "Netherlands",
        35: "North Macedonia",
        36: "Norway",
        37: "Poland",
        38: "Portugal",
        39: "Romania",
        40: "Russia",
        41: "San Marino",
        42: "Serbia",
        43: "Slovakia",
        44: "Slovenia",
        45: "Spain",
        46: "Sweden",
        47: "Switzerland",
        48: "Turkey",
        49: "Ukraine",
        50: "United Kingdom",
        51: "Vatican City",
    },
}


# DE10 – numeric per activity (hours per workday)
DE10 = {
    "xaxis_title": "Activity",
    "yaxis_title": "Average hours per workday",
    "plot_type": "average",
    "sub_map": {
        1: "career-focused activities",
        3: "household-related duties",
        4: "childcare-related duties",
        5: "other care-related duties",
        6: "social activities",
        7: "recreational activities",
        9: "sleeping",
    },
}


DE11 = DE10


# DE12 – single choice
DE12 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Never",
        2: "Rarely (1–2 days per month)",
        3: "Occasionally (1–2 days per week)",
        4: "Frequently (3–4 days per week)",
        5: "Always (5 days per week)",
    },
}

#####################

# DE13a – CV file upload
DE13a = {
    "type": "file_upload",
    "description": "Whether the participant uploaded a CV file.",
}


# DE13b – academic profile links
DE13b = {
    "type": "url_fields",
    "columns": {
        "Google Scholar": "DE13b_1",
        "ORCID": "DE13b_2",
        "ResearchGate": "DE13b_3",
        "Web of Science": "DE13b_4",
        "Scopus": "DE13b_5",
        "OpenAlex": "DE13b_6",
        "CV URL": "DE13b_7",
    },
}


DE13 = {
    "type": "optional_numeric_metrics",
    "columns": {
        "total_publications": "DE13_1",
        "total_citations": "DE13_2",
        "h_index": "DE13_3",
        "i10_index": "DE13_4",
        "unique_coauthors": "DE13_5",
        "research_interest_score": "DE13_6",
        "total_awarded_grants": "DE13_7",
    },
}


########################


DE14 = {
    "value_map": {1: "Woman", 2: "Man", 3: "Non-binary person"},
    "row_map": {1: "Parent 1", 2: "Parent 2"},
}


DE15 = {
    "value_map": {
        1: "Elementary: 0-4 years",
        2: "Elementary: 5-8 years",
        3: "High School: 1-3 years",
        4: "High School: 4 or more years",
        5: "College: 1-3 years",
        6: "College: 4 or more years",
        7: "Master's or professional degree",
        8: "Doctoral degree",
        9: "Dont know",
    },
    # "row_map": {1: "Parent 1", 2: "Parent 2"},
}


DE16 = {
    "value_map": {
        1: "Employed",
        2: "Not employed: stay-at-home parent",
        3: "Not employed: could not find a job",
        4: "Not employed: other reason (e.g., retired, illness, ...)",
        5: "Dont know or something else",
    },
    # "row_map": {1: "Parent 1", 2: "Parent 2"},
}


# DE17 — Partner/spouse gender identity
DE17 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Woman",
        2: "Man",
        3: "Non-binary person",
        4: "Prefer not to answer",
    },
}

# DE18 — Partner/spouse primary occupation
DE18 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Employed full-time",
        2: "Employed part-time",
        3: "Self-employed",
        4: "Unemployed",
        5: "Homemaker",
        6: "Student",
        7: "Retired",
        8: "Other (please specify)",
    },
}

# DE19 — Is your partner/spouse currently an academic?
DE19 = {
    "plot_type": "categorical",
    "value_map": {1: "Yes", 2: "No", 3: "Other (please specify)"},
}

# DE20 — Does your partner/spouse hold a PhD. or doctorate degree?
DE20 = {"plot_type": "categorical", "value_map": {1: "Yes", 2: "No"}}

# DE21
DE21 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Yes, a lot more",
        2: "Yes, slightly more",
        3: "No, slightly less",
        4: "No, a lot less",
        5: "No, my partner doesn't have an income",
    },
}

# numeric
DE22 = {
    "plot_type": "continuous",
    "x_label": "Number of children",
}

# DE23 – matrix about child birth years and countries
DE23 = {
    "row_map": {
        i: f"{i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'} child"
        for i in range(1, 11)
    },
    "sub_map": {1: "Year (YYYY)", 2: "Country"},
    "value_map": {
        # Could define allowed year range here, or validate separately
        "year_range": (1900, 2025),
        # "country_map": COUNTRY_MAP  # ← from DE5 and DE6
    },
}


# DE24 – multiple choice: reasons for not having children
DE24 = {
    "plot_type": "categorical",
    "value_map": {
        1: "I simply don’t want kids",
        2: "Medical reasons",
        3: "Financial reasons",
        4: "Negative impact on career advancement",
        5: "No partner or lack of a supportive partner",
        6: "Age",
        7: "State of the world",
        8: "Climate change / the environment",
        9: "Partner doesn’t want kids",
        10: "Other reasons",
    },
}


# PL1 – matrix: paid parental leave policy by academic role
PL1 = {
    "row_map": {
        1: "PhD students",
        2: "Postdocs",
        3: "Faculty (untenured)",
        4: "Faculty (tenure-track)",
        5: "Faculty (tenured)",
    },
    "value_map": {
        1: "No",
        2: "Yes, teaching relief only",
        3: "Yes, teaching and service relief",
        4: "Yes, full relief of duties",
        5: "Don't know",
    },
}


PL2 = {
    "row_map": {
        1: "PhD students",
        2: "Postdocs",
        3: "Faculty (untenured)",
        4: "Faculty (tenure-track)",
        5: "Faculty (tenured)",
    },
    "sub_map": {1: "Weeks", 2: "Months", 3: "Quarters", 4: "Semesters"},
    "value_map": {
        "min_value": 0,
        "max_value": 52,
    },
    "value_transform": unified_time_to_weeks,
}

PL3 = {
    "plot_type": "categorical",
    "value_map": {
        1: "There is no need for it",
        2: "Teaching relief only",
        3: "Teaching and service relief",
        4: "Full relief of duties",
        5: "Other",
    },
}


PL4 = {
    "row_map": {1: "PhD students", 2: "Postdocs", 3: "Professors"},
    "sub_map": {1: "Maternal (mother)", 2: "Paternal (father)"},
    "value_map": {
        "min_value": 0,
        "max_value": 36,  # assuming max 3 years; adjust based on actual data
    },
}


PL5 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Men and women should be offered the same unpaid parental leave",
        2: "Women should get more",
        3: "Men should get more",
        4: "Something else",
    },
}


PL6 = {
    "row_map": {
        str(
            i
        ): f"Your {i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'} child"
        for i in range(1, 10)
    }
    | {
        10: "Your 10th child (if you have more than 10 kids, please consider the youngest)"
    },
    "sub_map": {
        1: "No, I did not take the leave",
        2: "Yes, and I did not do anything work-related during that time",
        3: "Yes, and I spent up to 1/3 of that time on work-related activities",
        4: "Yes, and I spent about half of that time on work-related activities",
        5: "Yes, and I spent at least 2/3 of that time on work-related activities",
        6: "Not applicable",
    },
}


PL7 = {
    "row_map": {
        str(i): f"{i}{'st' if i==1 else 'nd' if i==2 else 'rd' if i==3 else 'th'} child"
        for i in range(1, 10)
    }
    | {10: "10th child (youngest if more than 10)"},
    "sub_map": {1: "Weeks", 2: "Months", 3: "Quarters", 4: "Semesters"},
    "value_transform": unified_time_to_weeks,
}


PL8 = {
    "plot_type": "categorical",
    "value_map": {
        1: "No",
        2: "Yes, but don't know how long",
        3: "Yes (please, enter how many years per child in numeric digits)",
        4: "Don't know",
    },
}


# PL10 – single choice
PL10 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Yes, much better",
        2: "Yes, slightly better",
        3: "Just the bare minimum",
        4: "Don't know",
    },
}

# CS2 – single choice
CS2 = {
    "plot_type": "categorical",
    "value_map": {
        1: "Yes, much better",
        2: "Yes, slightly better",
        3: "Just the bare minimum",
        4: "Don't know",
    },
}

# CS1 – matrix question about each child
CS1 = {
    "value_map_1": {1: "No", 2: "Yes", 3: "Don't know"},
    "value_map_2": {1: "No", 2: "Yes", 3: "Don't remember", 4: "Not applicable"},
    "row_map": {
        str(
            i
        ): f"Your {i}{'st' if i==1 else 'nd' if i==2 else 'rd' if i==3 else 'th'} child"
        for i in range(1, 11)
    },
    "sub_map": {1: "Childcare provided", 2: "Did you use it?"},
}

# CS3 – matrix: rating parental policies across 51 countries
CS3 = {
    "value_map": {
        1: "Very good policies",
        2: "Good policies",
        3: "Bad policies",
        4: "Very bad policies",
        5: "Don't know",
    },
    "row_map": {
        str(i): country
        for i, country in enumerate(
            [
                "Albania",
                "Andorra",
                "Armenia",
                "Austria",
                "Azerbaijan",
                "Belarus",
                "Belgium",
                "Bosnia and Herzegovina",
                "Bulgaria",
                "Croatia",
                "Cyprus",
                "Czech Republic",
                "Denmark",
                "Estonia",
                "Finland",
                "France",
                "Georgia",
                "Germany",
                "Greece",
                "Hungary",
                "Iceland",
                "Ireland",
                "Italy",
                "Kazakhstan",
                "Kosovo",
                "Latvia",
                "Liechtenstein",
                "Lithuania",
                "Luxembourg",
                "Malta",
                "Moldova",
                "Monaco",
                "Montenegro",
                "Netherlands",
                "North Macedonia (formerly Macedonia)",
                "Norway",
                "Poland",
                "Portugal",
                "Romania",
                "Russia",
                "San Marino",
                "Serbia",
                "Slovakia",
                "Slovenia",
                "Spain",
                "Sweden",
                "Switzerland",
                "Turkey",
                "Ukraine",
                "United Kingdom",
                "Vatican City (Holy See)",
            ],
            start=1,
        )
    },
}
