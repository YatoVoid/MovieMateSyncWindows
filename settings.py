
import json
def load_settings():
    with open("./settings.json", 'r') as file:
        settings = json.load(file)
    return settings

settings = load_settings()

font_sizes = settings['fonts']['sizes']
default_font_family = settings['fonts']['default']
default_appearance_mode = settings["themes"]["available"][1]
default_color_theme = settings["themes"]["available"][2]
default_server_port = settings['server']['default_port']