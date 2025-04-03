import re

MAX_NORMAL_MESSAGE = 600
MAX_EMBED_TITLE = 30
MAX_EMBED_DESCRIPTION = 600
MAX_EMBED_FOOTER = 30
MAX_FIELD_NAME = 30
MAX_FIELD_VALUE = 200
MAX_FIELDS = 25

COLORS = {
    "default": (0x3498db, "Azul", "🔵"),
    "red": (0xe74c3c, "Rojo", "🔴"),
    "green": (0x2ecc71, "Verde", "🟢"),
    "yellow": (0xf1c40f, "Amarillo", "🟡"),
    "orange": (0xe67e22, "Naranja", "🟠"),
    "purple": (0x9b59b6, "Morado", "🟣"),
    "pink": (0xff6b81, "Rosa", "🌸"),
    "gray": (0x95a5a6, "Gris", "⚪"),
    "black": (0x34495e, "Negro", "⚫"),
    "white": (0xecf0f1, "Blanco", "⬜"),
}

LOG_TYPES = {
    "ban": {
        "name": "Logs de baneo de usuarios",
        "params": ["{userid}", "{usertag}", "{mod}", "{modid}", "{modtag}", "{reason}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "kick": {
        "name": "Logs de expulsión de usuarios",
        "params": ["{userid}", "{usertag}", "{mod}", "{modid}", "{modtag}", "{reason}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "unban": {
        "name": "Logs de desbaneo de usuarios",
        "params": ["{userid}", "{usertag}", "{modtag}", "{modid}", "{mod}"],
        "footer_params": ["{userid}", "{usertag}", "{modtag}", "{modid}"]
    },
    "enter": {
        "name": "Logs de entrada de usuarios",
        "params": ["{userid}", "{usertag}", "{user}", "{accage}"],
        "footer_params": ["{userid}", "{usertag}", "{user}"]
    },
    "leave": {
        "name": "Logs de salida de usuarios",
        "params": ["{userid}", "{usertag}"],
        "footer_params": ["{userid}", "{usertag}"]
    },
    "del_msg": {
        "name": "Logs de mensajes eliminados",
        "params": ["{del_msg}", "{usertag}", "{userid}", "{user}", "{channel}", "{channelid}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"]
    },
    "edited_msg": {
        "name": "Logs de mensajes editados",
        "params": ["{user}", "{userid}", "{usertag}", "{channel}", "{channelid}", "{old_msg}", "{new_msg}"],
        "footer_params": ["{userid}", "{usertag}", "{channelid}"]
    },
    "warn": {
        "name": "Logs de advertencias",
        "params": ["{user}", "{userid}", "{usertag}", "{reason}", "{mod}", "{modtag}", "{modid}", "{warnid}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "unwarn": {
        "name": "Logs de eliminación de advertencias",
        "params": ["{user}", "{userid}", "{usertag}", "{reason}", "{mod}", "{modtag}", "{modid}", "{warnid}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    }
}

VALID_IMAGE_PARAMS = ["{servericon}", "{useravatar}"]

def validate_message_params(log_type, message, is_footer=False):
    return True, "Parámetros válidos"


def process_newlines(text):
    if text is None:
        return None
    return text.replace("{\\n}", "\n")


def is_valid_url(url):
    if not url:
        return False
    url_pattern = re.compile(
        r'^(https?://)?'
        r'([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}'
        r'(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?'
        r'$'
    )
    return bool(url_pattern.match(url)) or url in VALID_IMAGE_PARAMS


def is_valid_image_param(param):
    return param in VALID_IMAGE_PARAMS or is_valid_url(param)