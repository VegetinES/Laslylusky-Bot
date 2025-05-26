import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import asyncio
import time
import base64
from typing import Optional
from collections import deque
import os

class CheckVirus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("VIRUSTOTAL_API_KEY")
        
        self.minute_requests = deque(maxlen=4)
        self.day_requests = deque(maxlen=500)
        self.month_requests = deque(maxlen=15500)
        
        self.minute_expiry = 60
        self.day_expiry = 86400
        self.month_expiry = 2592000
    
    def _can_make_request(self):
        current_time = time.time()
        
        while self.minute_requests and current_time - self.minute_requests[0] > self.minute_expiry:
            self.minute_requests.popleft()
        
        while self.day_requests and current_time - self.day_requests[0] > self.day_expiry:
            self.day_requests.popleft()
        
        while self.month_requests and current_time - self.month_requests[0] > self.month_expiry:
            self.month_requests.popleft()
        
        if (len(self.minute_requests) >= 4 or 
            len(self.day_requests) >= 500 or 
            len(self.month_requests) >= 15500):
            return False
        
        return True
    
    def _add_request(self):
        current_time = time.time()
        self.minute_requests.append(current_time)
        self.day_requests.append(current_time)
        self.month_requests.append(current_time)
    
    async def _check_file(self, file_content, file_name):
        if not self._can_make_request():
            return None,
        
        self._add_request()
        
        headers = {"x-apikey": self.api_key}
        
        try:
            async with aiohttp.ClientSession() as session:
                form = aiohttp.FormData()
                form.add_field('file', file_content, filename=file_name)
                
                async with session.post(
                    "https://www.virustotal.com/api/v3/files",
                    headers=headers,
                    data=form
                ) as response:
                    if response.status != 200:
                        return None, f"Error al subir el archivo: {response.status}"
                    
                    upload_result = await response.json()
                    analysis_id = upload_result.get("data", {}).get("id")
                    
                    if not analysis_id:
                        return None, "No se pudo obtener el ID de análisis."
                    
                    for _ in range(20):
                        await asyncio.sleep(5)  
                        
                        if not self._can_make_request():
                            continue
                        
                        self._add_request()
                        
                        async with session.get(
                            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                            headers=headers
                        ) as analysis_response:
                            if analysis_response.status != 200:
                                continue
                            
                            analysis_result = await analysis_response.json()
                            status = analysis_result.get("data", {}).get("attributes", {}).get("status")
                            
                            if status == "completed":
                                file_id = None
                                if "meta" in analysis_result and "file_info" in analysis_result["meta"]:
                                    file_id = analysis_result["meta"]["file_info"].get("sha256")
                                
                                analysis_result["file_id"] = file_id
                                analysis_result["file_name"] = file_name
                                
                                return analysis_result, None
                    
                    return None, "El análisis tardó demasiado tiempo en completarse."
        
        except Exception as e:
            return None, f"Error al analizar el archivo: {str(e)}"
    
    async def _check_url(self, url):
        if not self._can_make_request():
            return None, "Se ha alcanzado el límite de solicitudes a VirusTotal. Por favor, inténtalo más tarde."
        
        self._add_request()
        
        headers = {
            "x-apikey": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = f"url={url}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://www.virustotal.com/api/v3/urls",
                    headers=headers,
                    data=data
                ) as response:
                    if response.status != 200:
                        return None, f"Error al enviar la URL: {response.status}"
                    
                    result = await response.json()
                    analysis_id = result.get("data", {}).get("id")
                    
                    if not analysis_id:
                        return None, "No se pudo obtener el ID de análisis."
                    
                    for _ in range(20):
                        await asyncio.sleep(5)
                        
                        if not self._can_make_request():
                            continue
                        
                        self._add_request()
                        
                        async with session.get(
                            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                            headers=headers
                        ) as analysis_response:
                            if analysis_response.status != 200:
                                continue
                            
                            analysis_result = await analysis_response.json()
                            status = analysis_result.get("data", {}).get("attributes", {}).get("status")
                            
                            if status == "completed":
                                analysis_result["url"] = url
                                
                                if analysis_id.startswith("u-"):
                                    url_id = analysis_id.split("-")[1]
                                    analysis_result["url_id"] = url_id
                                else:
                                    url_bytes = url.encode('utf-8')
                                    url_base64 = base64.urlsafe_b64encode(url_bytes).decode('utf-8').rstrip("=")
                                    analysis_result["url_id"] = url_base64
                                
                                return analysis_result, None
                    
                    return None, "El análisis tardó demasiado tiempo en completarse."
        
        except Exception as e:
            return None, f"Error al analizar la URL: {str(e)}"
    
    def _create_result_embed(self, result, is_file=True):
        attributes = result.get("data", {}).get("attributes", {})
        stats = attributes.get("stats", {})
        results = attributes.get("results", {})
        
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        total_engines = sum(stats.values())
        
        if malicious > 3 or (malicious + suspicious) > 5:
            color = discord.Color.red()
            threat_level = "⚠️ **ALTO RIESGO**"
        elif malicious > 0 or suspicious > 2:
            color = discord.Color.orange()
            threat_level = "⚠️ **PRECAUCIÓN**"
        else:
            color = discord.Color.green()
            threat_level = "✅ **SEGURO**"
        
        if is_file:
            file_name = result.get("file_name", "Archivo desconocido")
            file_id = result.get("file_id", "Desconocido")
            
            embed = discord.Embed(
                title=f"Resultado del análisis para: {file_name}",
                color=color,
                description=f"Nivel de amenaza: {threat_level}\n\n"
                            f"**SHA-256:** `{file_id}`\n\n"
                            f"**Detecciones:** {malicious} maliciosas, {suspicious} sospechosas de {total_engines} motores"
            )
            
            embed.add_field(
                name="Ver informe completo",
                value=f"[VirusTotal Report](https://www.virustotal.com/gui/file/{file_id})",
                inline=False
            )
        else:
            url = result.get("url", "URL desconocida")
            url_id = result.get("url_id", "")
            
            embed = discord.Embed(
                title=f"Resultado del análisis para: {url}",
                color=color,
                description=f"Nivel de amenaza: {threat_level}\n\n"
                            f"**Detecciones:** {malicious} maliciosas, {suspicious} sospechosas de {total_engines} motores"
            )
            
            embed.add_field(
                name="Ver informe completo",
                value=f"[VirusTotal Report](https://www.virustotal.com/gui/url/{url_id})",
                inline=False
            )
        
        if malicious > 0 or suspicious > 0:
            detections = []
            
            for engine_name, engine_result in results.items():
                result_category = engine_result.get("category", "")
                if result_category in ["malicious", "suspicious"]:
                    result_desc = engine_result.get("result", "No hay descripción")
                    detections.append(f"• **{engine_name}**: {result_desc}")
                
                if len(detections) >= 5:
                    break
            
            if detections:
                embed.add_field(
                    name="Principales detecciones",
                    value="\n".join(detections),
                    inline=False
                )
        
        embed.set_footer(text="Análisis realizado con VirusTotal", 
                        icon_url="https://www.virustotal.com/gui/images/favicon.png")
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @app_commands.command(name="comprobar-virus", description="Comprueba si un archivo o enlace contiene virus o malware")
    @app_commands.describe(
        archivo="Archivo a analizar",
        enlace="URL a analizar"
    )
    async def comprobar_virus(
        self, 
        interaction: discord.Interaction, 
        archivo: Optional[discord.Attachment] = None,
        enlace: Optional[str] = None
    ):
        if (archivo is None and enlace is None) or (archivo is not None and enlace is not None):
            await interaction.response.send_message(
                "Debes proporcionar un archivo **o** un enlace, pero no ambos a la vez.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(thinking=True)
        
        if archivo:
            if archivo.size > 32 * 1024 * 1024:
                await interaction.followup.send(
                    "El archivo es demasiado grande. El tamaño máximo permitido es de 32MB."
                )
                return
            
            if not self._can_make_request():
                await interaction.followup.send(
                    "Se ha alcanzado el límite de solicitudes a VirusTotal. Por favor, inténtalo más tarde."
                )
                return
            
            try:
                file_content = await archivo.read()
                result, error = await self._check_file(file_content, archivo.filename)
                
                if error:
                    await interaction.followup.send(f"Error: {error}")
                    return
                
                embed = self._create_result_embed(result, is_file=True)
                await interaction.followup.send(embed=embed)
            
            except Exception as e:
                await interaction.followup.send(f"Error inesperado al analizar el archivo: {str(e)}")
        
        elif enlace:
            if not self._can_make_request():
                await interaction.followup.send(
                    "Se ha alcanzado el límite de solicitudes a VirusTotal. Por favor, inténtalo más tarde."
                )
                return
            
            try:
                if not enlace.startswith(('http://', 'https://')):
                    await interaction.followup.send(
                        "El enlace debe comenzar con 'http://' o 'https://'."
                    )
                    return
                
                result, error = await self._check_url(enlace)
                
                if error:
                    await interaction.followup.send(f"Error: {error}")
                    return
                
                embed = self._create_result_embed(result, is_file=False)
                await interaction.followup.send(embed=embed)
            
            except Exception as e:
                await interaction.followup.send(f"Error inesperado al analizar el enlace: {str(e)}")

async def setup(bot):
    await bot.add_cog(CheckVirus(bot))
