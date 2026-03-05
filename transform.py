import json

MAP = {
    "Bg Fill": {
        "General": ["semantic", "background", "general"],
        "Card": ["semantic", "background", "card"],
        "Modal": ["semantic", "background", "modal"],
        "Section in modal": ["semantic", "background", "modal_section"],
        "In section in a modal": ["semantic", "background", "modal_section_inner"]
    },
    "Text": {
        "Core": ["semantic", "text", "core"],
        "Primary": ["semantic", "text", "primary"],
        "Secondary": ["semantic", "text", "secondary"],
        "Link or button": ["semantic", "text", "action"],
        "Placeholder": ["semantic", "text", "placeholder"]
    },
    "Stoke": {
        "Icon stroke": ["semantic", "stroke", "icon_primary"],
        "Icon stroke secondary": ["semantic", "stroke", "icon_secondary"],
        "Boarder": ["semantic", "border", "default"]
    },
    "Fill": {
        "Icon,Chip": ["semantic", "fill", "icon_chip"],
        "Fill B": ["semantic", "fill", "secondary"],
        "Fill C": ["semantic", "fill", "tertiary"],
        "Modal backdrop": ["semantic", "background", "backdrop"],
        "Logo": ["semantic", "fill", "logo"],
        "Color": ["semantic", "fill", "color_1"],
        "Color 2": ["semantic", "fill", "color_2"]
    },
    "*For linear gradient use": {
        "General bkg linear-1": ["semantic", "gradient", "general_1"],
        "General bkg linear-2": ["semantic", "gradient", "general_2"],
        "Token main bkg linear-1": ["semantic", "gradient", "main_1"],
        "Token main bkg linear-2": ["semantic", "gradient", "main_2"],
        "XAUT CARD BKG Linear -1": ["semantic", "gradient", "xaut_card_1"],
        "XAUT CARD BKG Linear - 2": ["semantic", "gradient", "xaut_card_2"],
        "Bar backdrop linear-1": ["semantic", "gradient", "bar_backdrop_1"],
        "Bar backdrop linear-2": ["semantic", "gradient", "bar_backdrop_2"]
    }
}

def set_nested(d, path, value):
    for key in path[:-1]:
        d = d.setdefault(key, {})
    d[path[-1]] = value

def transform_theme(theme_data):
    new_theme = {}
    for group, items in theme_data.items():
        if group in MAP:
            for item_key, current_val in items.items():
                if item_key in MAP[group]:
                    path = MAP[group][item_key]
                    set_nested(new_theme, path, current_val)
                else:
                    # Fallback
                    set_nested(new_theme, ["semantic", "unmapped", item_key], current_val)
        else:
             # Just keep what's not in MAP
             new_theme[group] = items
    return new_theme

with open('source/tokens.json', 'r') as f:
    data = json.load(f)

data['Light'] = transform_theme(data['Light'])
data['Dark'] = transform_theme(data['Dark'])

with open('source/tokens.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Semantic transformation completed.")
