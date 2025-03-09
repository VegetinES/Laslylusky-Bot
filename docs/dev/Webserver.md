# CONFIGURACIÓN WEB HTTP

Instalar Nginx
```bash
sudo apt update
sudo apt install nginx
```

Crear configuración para el sitio web 
```bash
sudo nano /etc/nginx/sites-available/dominio
```

Configuración:
```bash
server {
    listen 80;
    server_name dominio.com www.dominio.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Crear enlace simbólico
```bash
sudo ln -s /etc/nginx/sites-available/dominio /etc/nginx/sites-enabled/
```

Verificar configuración
```bash
sudo nginx -t
```

Reiniciar Nginx
```bash
sudo systemctl restart nginx
```

---

## Importante
```txt
DNS Importante

Tipo: A
Nombre: dominio.com
Valor: (IP Pública)
TTL: (valor por defecto)

Tipo: CNAME
Nombre: www.dominio.com
Valor: (dominio completo)
TTL: (valor por defecto)
```

# CONFIGURACIÓN HTTPS

Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

Obtener certificado SSL
```bash
sudo certbot --nginx -d dominio.com -d www.dominio.com
```

Configurar renovación automática
```bash
sudo crontab -e

# Esta línea dentro:
0 0 * * 1 certbot renew --quiet && systemctl reload nginx
# Se renovará cada lunes a medianoche y reinicando Nginx para aplicar los cambios
```