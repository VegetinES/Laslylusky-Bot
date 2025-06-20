from database.get import get_server_data
import discord

class PermissionChecker:
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    def get_user_roles_in_guild(self, guild_id, user_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return []
            
            member = guild.get_member(int(user_id))
            if not member:
                return []
            
            return [str(role.id) for role in member.roles]
        except:
            return []
    
    def check_discord_permissions(self, guild_permissions):
        MANAGE_GUILD = 0x20
        ADMINISTRATOR = 0x8
        
        permissions = int(guild_permissions)
        return (permissions & MANAGE_GUILD) or (permissions & ADMINISTRATOR)
    
    def check_bot_permissions(self, guild_id, user_id):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return False
            
            perms = server_data.get('perms', {})
            user_roles = self.get_user_roles_in_guild(guild_id, user_id)
            
            target_permissions = ['admin-roles', 'admin-users', 'mg-srv-roles', 'mg-srv-users']
            
            for perm in target_permissions:
                if perm.endswith('-roles'):
                    role_list = perms.get(perm, [])
                    if any(str(role_id) in user_roles for role_id in role_list if str(role_id) != '0'):
                        return True
                
                elif perm.endswith('-users'):
                    user_list = perms.get(perm, [])
                    if str(user_id) in [str(x) for x in user_list] and str(user_id) != '0':
                        return True
            
            return False
        except Exception as e:
            print(f"Error verificando permisos del bot: {e}")
            return False
    
    def get_all_manageable_servers(self, user_guilds, user_id):
        if not self.bot:
            return []
        
        bot_guilds = {str(guild.id): guild for guild in self.bot.guilds}
        manageable_servers = []
        
        for guild in user_guilds:
            guild_id = str(guild['id'])
            
            has_discord_perms = self.check_discord_permissions(guild['permissions'])
            has_bot_perms = False
            bot_present = guild_id in bot_guilds
            
            if bot_present:
                has_bot_perms = self.check_bot_permissions(guild_id, user_id)
            
            if has_discord_perms or has_bot_perms:
                guild['bot_present'] = bot_present
                manageable_servers.append(guild)
        
        return manageable_servers
    
    def get_manageable_servers(self, user_guilds, user_id):
        if not self.bot:
            return []
        
        bot_guilds = {str(guild.id): guild for guild in self.bot.guilds}
        manageable_servers = []
        
        for guild in user_guilds:
            guild_id = str(guild['id'])
            
            if guild_id not in bot_guilds:
                continue
            
            has_discord_perms = self.check_discord_permissions(guild['permissions'])
            
            has_bot_perms = self.check_bot_permissions(guild_id, user_id)
            
            if has_discord_perms or has_bot_perms:
                manageable_servers.append(guild)
        
        return manageable_servers

def create_permission_checker(bot_instance):
    return PermissionChecker(bot_instance)