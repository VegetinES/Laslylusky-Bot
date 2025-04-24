COLORS = {
    "default": (0x3498db, "Azul"),
    "blue": (0x3498db, "Azul"),
    "red": (0xff0000, "Rojo"),
    "green": (0x2ecc71, "Verde"),
    "yellow": (0xf1c40f, "Amarillo"),
    "orange": (0xe67e22, "Naranja"),
    "purple": (0x9b59b6, "Morado"),
    "pink": (0xff6b81, "Rosa"),
    "gray": (0x95a5a6, "Gris"),
    "black": (0x34495e, "Negro"),
    "white": (0xecf0f1, "Blanco"),
}

PERMISSIONS_DESCRIPTIONS = {
    "manage": {
        "name": "Gestionar tickets", 
        "description": "Permite el control total sobre los tickets, incluyendo ver, escribir, añadir/eliminar usuarios y archivar tickets."
    },
    "view": {
        "name": "Ver tickets", 
        "description": "Permite únicamente ver los tickets, sin poder escribir ni interactuar con los botones."
    }
}

DEFAULT_TICKET_CONFIG = {
    "ticket_channel": None,
    "log_channel": None,
    "auto_increment": {},
    "permissions": {
        "manage": {
            "roles": [],
            "users": []
        },
        "view": {
            "roles": [],
            "users": []
        }
    },
    "open_message": {
        "embed": True,
        "title": "Sistema de Tickets",
        "description": "Haz clic en el botón correspondiente para abrir un ticket de soporte.",
        "footer": "",
        "color": "blue",
        "fields": [],
        "image": {
            "url": "",
            "enabled": False
        },
        "thumbnail": {
            "url": "",
            "enabled": False
        },
        "buttons": [
            {
                "id": "default",
                "label": "Abrir Ticket",
                "emoji": "🎫",
                "style": 3,
                "name_format": "ticket-{id}",
                "description": "Abrir un ticket de soporte general"
            }
        ],
        "plain_message": ""
    },
    "opened_messages": {
        "default": {
            "embed": True,
            "title": "Ticket Abierto",
            "description": "Gracias por abrir un ticket. Un miembro del equipo te atenderá lo antes posible.",
            "footer": "",
            "color": "green",
            "fields": [],
            "image": {
                "url": "",
                "enabled": False
            },
            "thumbnail": {
                "url": "",
                "enabled": False
            },
            "plain_message": ""
        }
    }
}