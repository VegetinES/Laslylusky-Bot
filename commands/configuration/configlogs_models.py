from .configlogs_constants import (
    MAX_NORMAL_MESSAGE, MAX_EMBED_TITLE, MAX_EMBED_DESCRIPTION,
    MAX_EMBED_FOOTER, MAX_FIELD_NAME, MAX_FIELD_VALUE, MAX_FIELDS,
    COLORS, is_valid_image_param
)

class LogMessageModel:
    @staticmethod
    def create_default():
        return {
            "embed": False,
            "title": "",
            "description": "",
            "footer": "",
            "color": "default",
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
        }
    
    @staticmethod
    def update_field(message_data, field_id, name, value, inline=None):
        if "fields" not in message_data or not isinstance(message_data["fields"], dict):
            existing_fields = message_data.get("fields", {})
            if isinstance(existing_fields, dict):
                message_data["fields"] = existing_fields.copy()
            else:
                message_data["fields"] = {}
        
        field_id_str = str(field_id)

        current_inline = message_data["fields"].get(field_id_str, {}).get("inline", False)

        if len(name) > MAX_FIELD_NAME:
            return False, f"El nombre del campo es demasiado largo (máximo {MAX_FIELD_NAME} caracteres)"
            
        if len(value) > MAX_FIELD_VALUE:
            return False, f"El valor del campo es demasiado largo (máximo {MAX_FIELD_VALUE} caracteres)"

        if field_id_str not in message_data["fields"] and len(message_data["fields"]) >= MAX_FIELDS:
            return False, f"Se ha alcanzado el límite máximo de campos ({MAX_FIELDS})"
        
        message_data["fields"][field_id_str] = {
            "name": name,
            "value": value,
            "inline": current_inline if inline is None else inline
        }
        
        return True, "Campo actualizado correctamente"
        
    @staticmethod
    def delete_field(message_data, field_id):
        field_id_str = str(field_id)
        if "fields" in message_data and field_id_str in message_data["fields"]:
            del message_data["fields"][field_id_str]
            return True, "Campo eliminado correctamente"
        return False, "Campo no encontrado"
    
    @staticmethod
    def reorder_fields(message_data, new_order):
        if not message_data.get("fields"):
            return False, "No hay campos para reordenar"
        
        old_fields = message_data["fields"]
        new_fields = {}
        
        try:
            for new_id, old_id in enumerate(new_order, 1):
                old_id_str = str(old_id)
                if old_id_str in old_fields:
                    new_fields[str(new_id)] = old_fields[old_id_str]
            
            message_data["fields"] = new_fields
            return True, "Campos reordenados correctamente"
        except Exception as e:
            return False, f"Error al reordenar los campos: {e}"
    
    @staticmethod
    def validate_image_param(param):
        return is_valid_image_param(param)
    
    @staticmethod
    def from_legacy_format(message_format):
        model = LogMessageModel.create_default()
        
        if not message_format:
            return model
        
        if message_format.startswith("embed:"):
            model["embed"] = True
            parts = message_format[6:].split(" ")
            current_key = None
            current_value = []
            
            for part in parts:
                if part.startswith("tl:"):
                    if current_key:
                        if current_key == "title":
                            model["title"] = " ".join(current_value)
                        elif current_key == "description":
                            model["description"] = " ".join(current_value)
                        elif current_key == "footer":
                            model["footer"] = " ".join(current_value)
                    current_key = "title"
                    current_value = [part[3:]]
                elif part.startswith("dp:"):
                    if current_key:
                        if current_key == "title":
                            model["title"] = " ".join(current_value)
                        elif current_key == "description":
                            model["description"] = " ".join(current_value)
                        elif current_key == "footer":
                            model["footer"] = " ".join(current_value)
                    current_key = "description"
                    current_value = [part[3:]]
                elif part.startswith("ft:"):
                    if current_key:
                        if current_key == "title":
                            model["title"] = " ".join(current_value)
                        elif current_key == "description":
                            model["description"] = " ".join(current_value)
                        elif current_key == "footer":
                            model["footer"] = " ".join(current_value)
                    current_key = "footer"
                    current_value = [part[3:]]
                else:
                    current_value.append(part)
            
            if current_key:
                if current_key == "title":
                    model["title"] = " ".join(current_value)
                elif current_key == "description":
                    model["description"] = " ".join(current_value)
                elif current_key == "footer":
                    model["footer"] = " ".join(current_value)
        else:
            model["embed"] = False
            model["message"] = message_format
        
        return model