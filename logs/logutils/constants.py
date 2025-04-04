LOG_PARAMS = {
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
        "params": ["{userid}", "{usertag}", "{user}", "{accage}", "{acc_age}"],
        "footer_params": ["{userid}", "{usertag}", "{user}"]
    },
    "leave": {
        "name": "Logs de salida de usuarios",
        "params": ["{userid}", "{usertag}", "{acc_age}", "{server_age}"],
        "footer_params": ["{userid}", "{usertag}"]
    },
    "del_msg": {
        "name": "Logs de mensajes eliminados",
        "params": ["{del_msg}", "{usertag}", "{userid}", "{user}", "{channel}", "{channelid}", "{attached}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"]
    },
    "edited_msg": {
        "name": "Logs de mensajes editados",
        "params": ["{user}", "{userid}", "{usertag}", "{channel}", "{channelid}", "{old_msg}", "{new_msg}", "{attached}"],
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
    },
    "vc_enter": {
        "name": "Logs de entrada a canal de voz",
        "params": ["{user}", "{usertag}", "{userid}", "{channel}", "{channelid}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"]
    },
    "vc_leave": {
        "name": "Logs de salida de canal de voz",
        "params": ["{user}", "{usertag}", "{userid}", "{channel}", "{channelid}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"]
    },
    "add_usr_rol": {
        "name": "Logs de rol añadido a usuario",
        "params": ["{user}", "{usertag}", "{userid}", "{role}", "{roleid}"],
        "footer_params": ["{usertag}", "{userid}", "{roleid}"]
    },
    "rm_usr_rol": {
        "name": "Logs de rol eliminado a usuario",
        "params": ["{user}", "{usertag}", "{userid}", "{role}", "{roleid}"],
        "footer_params": ["{usertag}", "{userid}", "{roleid}"]
    },
    "add_ch": {
        "name": "Logs de canal creado",
        "params": ["{channel}", "{channelid}", "{category}"],
        "footer_params": ["{channelid}"]
    },
    "del_ch": {
        "name": "Logs de canal eliminado",
        "params": ["{channel}", "{channelid}", "{category}"],
        "footer_params": ["{channelid}"]
    },
    "changed_av": {
        "name": "Logs de cambio de avatar/nombre",
        "params": ["{user}", "{usertag}", "{userid}", "{old_avatar_link}", "{new_avatar_link}", "{old_name}", "{new_name}"],
        "footer_params": ["{usertag}", "{userid}"]
    }
}

VALID_IMAGE_PARAMS = ["{servericon}", "{useravatar}"]