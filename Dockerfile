FROM n8nio/n8n:latest

WORKDIR /data

COPY ./prueba_PayJoy.json /data/prueba_PayJoy.json

EXPOSE 5678

CMD ["n8n", "start", "--tunnel"]
