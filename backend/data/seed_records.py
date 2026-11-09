from datetime import date, timedelta

COMMODITIES_SEED = [
    {"name": "Tomato", "name_hi": "टमाटर"},
    {"name": "Potato", "name_hi": "आलू"},
    {"name": "Onion", "name_hi": "प्याज"}
]

MANDIS_SEED = [
    {"name": "Lucknow", "district": "Lucknow", "state": "Uttar Pradesh"},
    {"name": "Kanpur", "district": "Kanpur Nagar", "state": "Uttar Pradesh"},
    {"name": "Agra", "district": "Agra", "state": "Uttar Pradesh"}
]

def generate_sample_price_records():
    """Generates 30 days of realistic daily mandi prices up to today for Lucknow."""
    today = date.today()
    records = []

    # Tomato base price ~ 2200 Rs/quintal with natural daily variation
    tomato_base = [
        2100, 2150, 2120, 2200, 2250, 2300, 2280, 2350, 2400, 2380,
        2420, 2450, 2400, 2360, 2300, 2250, 2280, 2310, 2340, 2380,
        2410, 2450, 2480, 2520, 2500, 2460, 2490, 2530, 2560, 2580
    ]

    # Potato base price ~ 1400 Rs/quintal
    potato_base = [
        1350, 1360, 1380, 1370, 1390, 1400, 1420, 1410, 1400, 1430,
        1440, 1450, 1430, 1420, 1440, 1450, 1460, 1470, 1460, 1480,
        1490, 1500, 1490, 1510, 1520, 1510, 1530, 1540, 1530, 1550
    ]

    # Onion base price ~ 3100 Rs/quintal
    onion_base = [
        2900, 2950, 2920, 2980, 3020, 3050, 3080, 3120, 3100, 3150,
        3180, 3200, 3190, 3220, 3250, 3240, 3280, 3300, 3320, 3350,
        3340, 3360, 3390, 3420, 3400, 3440, 3460, 3480, 3500, 3520
    ]

    for i in range(30):
        record_date = today - timedelta(days=(29 - i))
        
        # Tomato
        modal_t = tomato_base[i]
        records.append({
            "commodity": "Tomato",
            "mandi": "Lucknow",
            "price_date": record_date,
            "min_price": modal_t - 200,
            "max_price": modal_t + 250,
            "modal_price": modal_t,
            "unit": "₹/Quintal",
            "source": "Agmarknet"
        })

        # Potato
        modal_p = potato_base[i]
        records.append({
            "commodity": "Potato",
            "mandi": "Lucknow",
            "price_date": record_date,
            "min_price": modal_p - 150,
            "max_price": modal_p + 180,
            "modal_price": modal_p,
            "unit": "₹/Quintal",
            "source": "Agmarknet"
        })

        # Onion
        modal_o = onion_base[i]
        records.append({
            "commodity": "Onion",
            "mandi": "Lucknow",
            "price_date": record_date,
            "min_price": modal_o - 250,
            "max_price": modal_o + 300,
            "modal_price": modal_o,
            "unit": "₹/Quintal",
            "source": "Agmarknet"
        })

    return records
