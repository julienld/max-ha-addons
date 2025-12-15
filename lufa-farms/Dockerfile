ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache python3 py3-requests py3-beautifulsoup4 py3-paho-mqtt

WORKDIR /app
COPY run.py /app/run.py
COPY client.py /app/client.py
COPY mqtt_client.py /app/mqtt_client.py
COPY run.sh /app/run.sh
RUN chmod a+x /app/run.sh

# Run the script
CMD [ "/app/run.sh" ]
