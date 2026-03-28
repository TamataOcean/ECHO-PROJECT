FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

# --- Dépendances système ---
RUN apt-get update && apt-get install -y \
    # Python
    python3 python3-pip python3-setuptools \
    # GStreamer + dépendances de compilation gstd
    git automake libtool pkg-config \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libglib2.0-dev libjson-glib-dev gtk-doc-tools \
    libncursesw5-dev libdaemon-dev libjansson-dev \
    libsoup2.4-dev libedit-dev \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    python3-gst-1.0 \
    meson ninja-build \
    # Outils réseau
    iputils-ping \
    cifs-utils \
    # Broker MQTT
    mosquitto \
    # Gestionnaire de processus
    supervisor \
    # Node.js (prérequis Node-RED)
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --- Node.js 20 LTS ---
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# --- Compilation gstd (identique au deploy/server_install.sh — section NEW PROCESS) ---
# meson build → ninja → install binaire → setup.py install pour pygstc Python
RUN git clone https://github.com/RidgeRun/gstd-1.x.git /tmp/gstd-1.x \
    && cd /tmp/gstd-1.x \
    && meson build \
    && ninja -C build \
    && ninja -C build install \
    && cd libgstc/python \
    && python3 setup.py install \
    && ldconfig \
    && rm -rf /tmp/gstd-1.x

# --- Dépendances Python ---
RUN pip3 install --no-cache-dir --break-system-packages paho-mqtt

# --- Node-RED + plugins ---
# Installé dans /usr/src/node-red (hors du volume /data) pour ne pas être
# écrasé par le bind mount. Node-RED résout les plugins depuis son propre
# répertoire node_modules, donc ils seront bien trouvés au démarrage.
RUN mkdir -p /usr/src/node-red \
    && cd /usr/src/node-red \
    && npm install --no-fund --no-audit \
        node-red@4.0.2 \
        node-red-node-ping \
        node-red-dashboard \
        node-red-contrib-fs-ops

# --- Répertoires runtime ---
RUN mkdir -p /app /data /app/EXPORT_VIDEOS /var/log/echo-project /run/mosquitto

# --- Copie des sources ---
COPY core/server.py /app/server.py
COPY core/pControler-from-JSON.py /app/pControler-from-JSON.py
COPY mount_nas.sh /app/mount_nas.sh
COPY update_nas_config.py /app/update_nas_config.py
RUN chmod +x /app/mount_nas.sh /app/update_nas_config.py
COPY mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf
COPY supervisord.conf /etc/supervisord.conf

WORKDIR /app

# Node-RED UI : 1880 | MQTT broker : 1883
EXPOSE 1880 1883

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.conf"]
