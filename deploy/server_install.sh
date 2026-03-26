echo "############################################# "
echo "######### Installation des packages ######### "
echo "############################################# "
echo "######### Mise à jour système"
sudo apt update
sudo apt upgrade

echo "######### Installation Mosquitto"
sudo apt install -y mosquitto

echo "######### Installation Git"
sudo apt-get -y install git

echo "######### Installation vlc"
sudo apt-get install vlc

# -------------------------
# Installation python
# -------------------------
echo "######### Installation python & dépendances"
sudo apt-get -y install python3-gst-1.0 gstreamer1.0-tools gstreamer1.0-plugins-good
sudo apt-get -y install python3-pip
sudo pip3 install paho-mqtt --break-system-packages

# -------------------------
# Installation Node-Red
# -------------------------
# Process > https://nodered.org/docs/getting-started/raspberrypi
cd
echo "######### Installation Node-Red"
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
echo "Adding Node-Red as a service"
sudo systemctl enable nodered.service
# Composant Ui 
npm install node-red-dashboard
# Composant pour accés aux fichiers du système
npm install node-red-contrib-fs-ops
# Ajout du flows de l'application 
sudo cp ~/code/ECHO-PROJECT/core/node-red/flows.json /home/pi/.node-red/flows.json
# Connection via : //localhost:1880/ui 

# -------------------------
# Installation GStreamer
# -------------------------
echo "######### Installation GStreamer client"
sudo apt-get -y install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

echo "######### Installation Gstreamer service"
cd
git clone https://github.com/RidgeRun/gstd-1.x.git
cd gstd-1.x/
sudo apt-get -y install automake libtool pkg-config libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libglib2.0-dev libjson-glib-dev gtk-doc-tools libncursesw5-dev libdaemon-dev libjansson-dev libsoup2.4-dev python3-pip libedit-dev
./autogen.sh 
./configure 

meson build 
ninja -C build
sudo ninja -C build install
pushd libgstc/python
./setup.py install --user
sudo ./setup.py install --user
gstd --version

# Ajout du service GSTD
sudo cp ~/code/ECHO-PROJECT/deploy/gstd.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gstd.service
sudo systemctl start gstd.service
echo "######### Gstd - Installation terminée"

# Ajout du service python server.py
echo "Server ECHO-PROJECT Installation"
sudo cp ~/code/ECHO-PROJECT/deploy/mqtt_server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mqtt_server.service
sudo systemctl start mqtt_server.service
echo "Installation Server ECHO-PROJECT terminée"

# -------------------------
#         VIDEO SPY 
# -------------------------
# Version Docker ( INOP avec Trixie ) 
# sudo docker run -d --name=AgentDVR -e PUID=1000 -e PGID=1000 -e TZ=America/New_York -e AGENTDVR_WEBUI_PORT=8090 -p 8090:8090 -p 3478:3478/udp -p 50000-50100:50000-50100/udp -v /appdata/AgentDVR/config/:/AgentDVR/Media/XML/ -v /appdata/AgentDVR/media/:/AgentDVR/Media/WebServerRoot/Media/ -v /appdata/AgentDVR/commands:/AgentDVR/Commands/ --restart unless-stopped mekayelanik/ispyagentdvr:latest
    
    sudo apt-get install curl
    curl -sL "https://www.ispyconnect.com/install" -o install_agent.sh && sudo bash install_agent.sh; rm install_agent.sh

When Agent DVR is installed access the local UI at http://localhost:8090
# Save config file from /home/pi/code/ECHO-PROJECT/deploy/iSpyConfig to /opt/AgentDVR/Media/XML
layout.json / objects.xml / config.xml

# -------------------------
# MAPPING WITH EXTERNAL NAS
# -------------------------
### Create dedicated directory
sudo mkdir /mnt/echonas
### Create credential to authenticate on shared directory ( defined on NAS via DSM )
touch /home/pi/.smbcredentials
echo "username=votre_utilisateur" >> /home/pi/.smbcredentials
echo "password=votre_password" >> /home/pi/.smbcredentials
chmod 0400 /home/pi/.smbcredentials

sudo mount -t cifs //[IP_NAS]/ECHO_VIDEOs /mnt/echonas -o credentials=/home/pi/.smbcredentials,vers=3.0,iocharset=utf8,uid=1000,gid=1000

### AUTO mount
sudo vi /etc/fstab 
# Ajouter la ligne suivante :
//[IP_NAS]/ECHO_VIDEOs /mnt/echonas cifs credentials=/home/pi/.smbcredentials,vers=3.0,iocharset=utf8,uid=1000,gid=1000

# --------------------------------
# Installation Samba ( OPTIONNEL )
# --------------------------------
# Partage sur le réseau ( en attendant le NAS )
sudo apt install samba -y

# a la fin du fichier /etc/samba/smb.conf ajouter : 
[Videos-Echo]
path = /home/pi/code/ECHO-PROJECT/EXPORT_VIDEOS
browseable = yes
writeable = yes
create mask = 0777
directory mask = 0777
public = yes
force user = pi
# ajoute un client 
sudo smbpasswd -a pi
# redémarrer le service
sudo systemctl restart smbd

# ---------------------------------
# Installation Docker ( OPTIONNEL )
# ---------------------------------
curl -fsSL https://get.docker.com -o get-docker.sh
export VERSION_CODENAME=bookworm
sudo -E sh get-docker.sh
sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bookworm stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker
docker compose version

# OPTION INSTALL WITH NVME disk
### Identifier le disque
lsblk
### Création du mount point
sudo mkdir /mnt/NVME
### Formatage du disque
sudo mkfs.ext4 /dev/nvme0n1
### Mounting SSD Disk
sudo mount /dev/nvme0n1 /mnt/NVME
### AUTO Mount
sudo vi /etc/fstab
# Add the following line at the end:
/dev/nvme0n1 /mnt/nvme ext4 defaults 0 2
### unmount ( if necessary )
sudo umount /mnt/NVME

