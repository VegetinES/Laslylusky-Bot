import re
import aiohttp

def chunk_message(message, chunk_size):
    return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

async def create_paste(content, title, api_key, user_key):
    try:
        if not api_key:
            return None

        data = {
            'api_dev_key': api_key,
            'api_option': 'paste',
            'api_paste_code': content,
            'api_paste_name': title,
            'api_paste_private': '1',
            'api_paste_expire_date': '1W'
        }
        
        if user_key:
            data['api_user_key'] = user_key

        async with aiohttp.ClientSession() as session:
            async with session.post('https://pastebin.com/api/api_post.php', data=data) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    error_text = await response.text()
                    print(f"Error de Pastebin: {error_text}")
                    return None
    except Exception as e:
        print(f"Error al crear paste: {e}")
        return None

def format_attachments(attachments):
    if not attachments:
        return "No hay adjuntos"
    
    result = []
    for attachment in attachments:
        url_parts = attachment.url.split('?')
        clean_url = url_parts[0]
        result.append(f"[{attachment.filename}]({clean_url})")
    
    return "\n".join(result)

def is_valid_url(url):
    if not url:
        return False
        
    url_pattern = re.compile(
        r'^(https?://)?'
        r'([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}'
        r'(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?'
        r'$'
    )
    return bool(url_pattern.match(url))