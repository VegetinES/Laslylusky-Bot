def get_data(guild):
    data = {
        "guild_id": guild,
        "default_cdm": ["help", "donate", "info", "invite", "privacidad", "updates", "savedatachat", "botsuggest", "bugreport", "laslylusky", "reset-chat", "config", "infracciones", "moderador", "recordatorio", "nivel", "voicesetup", "cumpleaños", "estadisticas-juegos", "comprobar-virus", "tos"],
        "act_cmd": ["serverinfo", "slowmode", "kill", "meme", "avatar", "servericon", "userinfo", "ban", "unban", "clear", "kick", "warn", "unwarn", "4k", "anal", "ass", "blowjob", "boobs", "hanal", "hass", "hboobs", "pgif", "pussy", "mcstatus", "mcuser", "hypixel", "hug", "massban", "embed", "8ball", "morse", "id", "trivia", "tictactoe", "ruletarusa", "insulto", "halago", "moneda", "dado", "buscaminas", "piedrapapeltijera", "ahorcado", "conecta4", "blackjack", "mute", "unmute", "2048"],
        "deact_cmd": [],
        "mute_role": 0,
        "perms": {
            "mg-ch-roles": [0],
            "mg-ch-users": [0],
            "admin-roles": [0],
            "admin-users": [0],
            "mg-rl-roles": [0],
            "mg-rl-user": [0],
            "mg-srv-roles": [0],
            "mg-srv-users": [0],
            "kick-roles": [0],
            "kick-users": [0],
            "ban-roles": [0],
            "ban-users": [0],
            "mute-roles": [0],
            "mute-users": [0],
            "deafen-roles": [0],
            "deafen-users": [0],
            "mg-msg-roles": [0],
            "mg-msg-users": [0],
            "warn-users": [0],
            "warn-roles": [0],
            "unwarn-users": [0],
            "unwarn-roles": [0]
        },
        "audit_logs": {
            "ban": {
                "log_channel": 0,
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False
            },
            "kick": {
                "log_channel": 0,
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False
            },
            "unban": {
                "log_channel": 0,
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False
            },
            "enter": {
                "log_channel": 0,
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False
            },
            "leave": {
                "log_channel": 0,
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False
            },
            "del_msg": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            }, 
            "edited_msg": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            },
            "warn": {
                "log_channel": 0,
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False
            },
            "unwarn": {
                "log_channel": 0,
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False
            },
            "vc_enter": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            },
            "vc_leave": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            },
            "add_usr_rol": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            },
            "rm_usr_rol": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            },
            "add_ch": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            },
            "del_ch": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            },
            "changed_av": { 
                "log_channel": 0, 
                "message": {
                    "embed": False,
                    "title": "",
                    "description": "",
                    "footer": "",
                    "color": "", 
                    "image": {
                        "has": False,
                        "param": ""
                    },
                    "thumbnail": {
                        "has": False,
                        "param": ""
                    },
                    "fields": {},
                    "message": ""
                },
                "activated": False 
            }
        },
        "tickets": {},
        "language": "es"
    }

    return data