import oracledb
import os
import json
import time

class Oracle:
    def __init__(self):
        self.instant_client_path = "/home/ubuntu/Laslylusky/instantclient"
        self.wallet_path = "/home/ubuntu/Laslylusky/wallet"
        self.connection = None
        self.cursor = None
    
    def connect(self):
        os.environ["TNS_ADMIN"] = self.wallet_path
        oracledb.init_oracle_client(lib_dir=self.instant_client_path)
        self.connection = oracledb.connect(
            user="ADMIN",
            password=f"{os.getenv('ADMIN')}",
            dsn="laslylusky_high",
            wallet_location=self.wallet_path,
            wallet_password=f"{os.getenv('ADMIN')}"
        )
        self.cursor = self.connection.cursor()
        print("Conexión establecida")

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
            print("Cursor cerrado")
        
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Conexión cerrada")

    def _get_data(self):
        if not self.cursor:
            raise Exception("No hay conexión establecida. Llama a connect() primero.")
            
        self.cursor.execute("SELECT json_document FROM infractions")
        row = self.cursor.fetchone()
        
        if not row:
            return {"guilds": {}, "next_warn_id": 1, "temp": 0}

        blob_data = row[0]
        json_str = blob_data.read().decode('utf-8')
        data = json.loads(json_str)

        if "next_warn_id" not in data:
            data["next_warn_id"] = 1
            
        if "temp" not in data:
            data["temp"] = 0
            
        return data

    def _save_data(self, data):
        if not self.cursor or not self.connection:
            raise Exception("No hay conexión establecida. Llama a connect() primero.")

        json_bytes = json.dumps(data).encode('utf-8')

        self.cursor.execute("UPDATE infractions SET json_document = :1, last_modified = CURRENT_TIMESTAMP", [json_bytes])
        self.connection.commit()

    def get(self, guild_id, user_id=None, infraction_type=None, warn_id=None):
        data = self._get_data()

        if guild_id not in data.get("guilds", {}):
            return {"error": f"El servidor {guild_id} no existe en la base de datos"}
        
        guild_data = data["guilds"][guild_id]

        if warn_id is not None:
            if "warns" not in guild_data:
                return {"error": f"No hay advertencias en el servidor {guild_id}"}
                
            for user_id, warnings in guild_data["warns"].items():
                for warn in warnings:
                    if warn.get("id") == warn_id:
                        return {"warn": warn, "user_id": user_id}
            
            return {"error": f"No se encontró la advertencia con ID {warn_id}"}

        if not infraction_type and not user_id:
            return guild_data

        if infraction_type and not user_id:
            if infraction_type not in guild_data:
                return {"error": f"No hay {infraction_type} en el servidor {guild_id}"}
            return {infraction_type: guild_data.get(infraction_type, {})}

        if user_id and not infraction_type:
            result = {}
            if "warns" in guild_data and user_id in guild_data["warns"]:
                result["warns"] = guild_data["warns"][user_id]
            if "bans" in guild_data and user_id in guild_data["bans"]:
                result["bans"] = guild_data["bans"][user_id]
            
            if not result:
                return {"error": f"No se encontraron infracciones para el usuario {user_id}"}
            return result

        if infraction_type and user_id:
            if infraction_type not in guild_data:
                return {"error": f"No hay {infraction_type} en el servidor {guild_id}"}
            
            if infraction_type == "warns":
                if user_id not in guild_data["warns"]:
                    return {"error": f"No hay advertencias para el usuario {user_id}"}
                return {"warns": guild_data["warns"][user_id]}
            
            elif infraction_type == "bans":
                if user_id not in guild_data["bans"]:
                    return {"error": f"No hay ban para el usuario {user_id}"}
                return {"bans": guild_data["bans"][user_id]}
    
    def insert(self, guild_id, user_id, mod_id, reason, action_type, timestamp=None):
        if not timestamp:
            timestamp = int(time.time())

        data = self._get_data()

        if guild_id not in data["guilds"]:
            data["guilds"][guild_id] = {"warns": {}, "bans": {}}

        guild_data = data["guilds"][guild_id]

        if action_type == "warn":
            if "warns" not in guild_data:
                guild_data["warns"] = {}
            
            if user_id not in guild_data["warns"]:
                guild_data["warns"][user_id] = []

            warn_id = data["next_warn_id"]
            data["next_warn_id"] += 1

            new_warn = {
                "id": warn_id,
                "mod": mod_id,
                "fecha": timestamp,
                "razón": reason
            }
            
            guild_data["warns"][user_id].append(new_warn)

            self._save_data(data)
            return {"success": True, "action": "warn", "warn_id": warn_id}
        
        elif action_type == "ban":
            if "bans" not in guild_data:
                guild_data["bans"] = {}

            guild_data["bans"][user_id] = {
                "mod": mod_id,
                "fecha": timestamp,
                "razón": reason
            }

            self._save_data(data)
            return {"success": True, "action": "ban"}
        
        else:
            return {"error": f"Tipo de acción '{action_type}' no reconocido"}

    def update(self, guild_id, user_id, action_type, warn_id=None, mod_id=None):
        data = self._get_data()

        if guild_id not in data.get("guilds", {}):
            return {"error": f"El servidor {guild_id} no existe en la base de datos"}
        
        guild_data = data["guilds"][guild_id]

        if action_type == "unwarn":
            if "warns" not in guild_data or user_id not in guild_data["warns"]:
                return {"error": f"No hay advertencias para el usuario {user_id}"}
            
            user_warns = guild_data["warns"][user_id]
            
            if not user_warns:
                return {"error": f"No hay advertencias para el usuario {user_id}"}

            if warn_id is not None:
                for i, warn in enumerate(user_warns):
                    if warn.get("id") == warn_id:
                        removed_warn = user_warns.pop(i)

                        if not user_warns:
                            del guild_data["warns"][user_id]

                        self._save_data(data)
                        return {"success": True, "action": "unwarn", "removed": removed_warn}
                
                return {"error": f"No se encontró la advertencia con ID {warn_id}"}

            else:
                removed_warn = user_warns.pop()
                
                if not user_warns:
                    del guild_data["warns"][user_id]

                self._save_data(data)
                return {"success": True, "action": "unwarn", "removed": removed_warn}
        
        elif action_type == "unban":
            if "bans" not in guild_data or user_id not in guild_data["bans"]:
                return {"error": f"El usuario {user_id} no está baneado"}
            
            removed_ban = guild_data["bans"].pop(user_id)
            
            self._save_data(data)
            return {"success": True, "action": "unban", "removed": removed_ban}
        
        else:
            return {"error": f"Tipo de acción '{action_type}' no reconocido"}

    def delete(self, guild_id):
        data = self._get_data()
        
        if guild_id not in data.get("guilds", {}):
            return {"error": f"El servidor {guild_id} no existe en la base de datos"}
        
        del data["guilds"][guild_id]
        
        self._save_data(data)
        return {"success": True, "action": "delete_guild"}
    
    def update_temp(self, value):
        data = self._get_data()
        data["temp"] = value
        self._save_data(data)
        return {"success": True, "action": "update_temp", "value": value}
    
    def get_temp(self):
        data = self._get_data()
        return {"temp": data.get("temp", 0)}
    
    def initialize_guild(self, guild_id):
        data = self._get_data()
        
        if guild_id in data.get("guilds", {}):
            return {"warning": f"El servidor {guild_id} ya existe en la base de datos"}
        
        data["guilds"][guild_id] = {
            "warns": {},
            "bans": {}
        }
        
        self._save_data(data)
        return {"success": True, "action": "initialize_guild", "guild_id": guild_id}
    
    def delete_guild(self, guild_id):
        return self.delete(guild_id)