FROM n8nio/n8n:latest

# Copia tu flujo
COPY prueba_PayJoy.json /home/node/.n8n/prueba_PayJoy.json

# Puerto que expondrá Render
EXPOSE 5678

# Variables de entorno no sensibles
ENV GENERIC_TIMEZONE=America/Bogota
ENV N8N_BASIC_AUTH_ACTIVE=true

# Ejecutar n8n como usuario node
USER node

# Comando para iniciar n8n
ENTRYPOINT ["n8n", "start"]
