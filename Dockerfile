FROM n8nio/n8n:latest

WORKDIR /data

# Copiamos tu flujo exportado
COPY ./prueba_PayJoy.json /data/prueba_PayJoy.json

EXPOSE 5678

# Importa el flujo y arranca n8n
CMD ["sh", "-c", "n8n import:workflow --input=/data/prueba_PayJoy.json && n8n start"]
