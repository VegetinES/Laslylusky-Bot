# Arrancando el servidor

## Crear entorno virtual
```bash
python3 -m venv host
```

## Activar el entorno virtual
```bash
source host/bin/activate
```

## Instalar las librerías
```bash
pip install -r requirements.txt
```

## Ejecutar el bot mediante nohup
```bash
nohup python3 -u main.py > bot_log.txt 2>&1 &
```

## Ver los cambios en tiempo real
```bash
tail -f bot_log.txt
```

## Ver el proceso
```bash
ps aux | grep main.py
```
