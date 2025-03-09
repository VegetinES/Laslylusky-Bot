# Configuración Música Ubuntu Server

## Actualizar el sistema
```bash
sudo apt update && sudo apt upgrade -y
```

## Instalar firefox, un entorno de escritorio y el servidor VNC
```bash
sudo apt install -y firefox xfce4 xfce4-goodies tightvncserver
```

## Iniciar Tightvncserver
```bash
vncserver
```

## Matamos el servidor VNC
```bash
vncserver -kill :1
```

## Editamos el archivo xstartup
```bash
nano ~/.vnc/xstartup
```

## Establecemos el siguiente contenido:
```bash
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
```

## Nos aseguramos que se puede ejecutar
```bash
chmod +x ~/.vnc/xstartup
```

## Ejecutamos el servidor VNC
```bash
vncserver :1
```

## Entramos y ejecutamos
```bash
xhost +
```

## Instalamos librerías ffmpeg necesarias
```bash
sudo apt install -y ffmpeg libavdevice-dev
```

## Creamos un systemd
```bash
sudo nano /etc/systemd/system/startup-once.service
```

## Agregamos el contenido
```bash
[Unit]
Description=Ejecutar comandos en el proximo reinicio
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/startup-once.sh
ExecStartPost=/bin/sh -c 'systemctl disable startup-once.service'

[Install]
WantedBy=multi-user.target
```

## Creamos el script
```bash
sudo nano /usr/local/bin/startup-once.sh
```

## Agregar contenido
```bash
#!/bin/bash
systemctl enable ssh
systemctl restart ssh
```

## Permisos de ejecución
```bash
sudo chmod +x /usr/local/bin/startup-once.sh
```

## Activamos servicio
```bash
sudo systemctl daemon-reload
sudo systemctl enable startup-once.service
```

## Eliminamos el servidor VNC y el entorno de escritorio
```bash
sudo apt remove --purge xfce4 xfce4-goodies tightvncserver
```

## Eliminamos dependencias innecesarias
```bash
sudo apt autoremove --purge
```

## Limpiamos la caché 
```bash
sudo apt clean
```

## Reiniciamos
```bash
sudo reboot now
```

## Comprobamos que salió bien
```bash
sudo systemctl status startup-once.service
```