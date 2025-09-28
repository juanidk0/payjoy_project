# Usa la imagen oficial de n8n
FROM n8nio/n8n:latest

# Copia tu flujo al directorio de n8n
COPY prueba_PayJoy.json /home/node/.n8n/prueba_PayJoy.json

# Puerto que expondrá Render
EXPOSE 5678

# Variables de entorno no sensibles por defecto
ENV GENERIC_TIMEZONE=America/Bogota
ENV N8N_BASIC_AUTH_ACTIVE=true

# Comando por defecto para iniciar n8n
CMD ["n8n"]
