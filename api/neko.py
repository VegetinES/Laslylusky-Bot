import requests

class NekoAPI:
    BASE_URL = "https://nekobot.xyz/api/image"
    
    @staticmethod
    async def get_image(image_type: str) -> tuple[bool, str]:
        try:
            response = requests.get(
                NekoAPI.BASE_URL,
                params={"type": image_type}
            )
            response.raise_for_status()
            return True, response.json()['message']
        except requests.exceptions.RequestException as e:
            print(f"Error in API request: {e}")
            return False, "Hubo un error al obtener la imagen."