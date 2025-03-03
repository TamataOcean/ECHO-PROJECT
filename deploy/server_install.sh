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

echo "######### Installation python & dépendances"
sudo apt-get -y install python3-gst-1.0 gstreamer1.0-tools gstreamer1.0-plugins-good
sudo apt-get -y install python3-pip
# pip3 install paho-mqtt > propduit une erreur
sudo pip3 install paho-mqtt --break-system-packages

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

echo "######### Installation GStreamer client"
sudo apt-get -y install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

echo "######### Installation Gstreamer service"
cd
git clone https://github.com/RidgeRun/gstd-1.x.git
cd gstd-1.x/
sudo apt-get -y install automake libtool pkg-config libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libglib2.0-dev libjson-glib-dev gtk-doc-tools libncursesw5-dev libdaemon-dev libjansson-dev libsoup2.4-dev python3-pip libedit-dev
./autogen.sh 
./configure 
make
make install
sudo make install
gstd --version
echo "######### Gstd - Installation terminée"

### NEW PROCESS mais je ne sais pas quelle ligne retirée de la précédente commande ;) 
meson build 
ninja -C build
sudo ninja -C build install
pushd libgstc/python
./setup.py install --user
sudo ./setup.py install --user

# Ajout du service GSTD
sudo cp ~/code/ECHO-PROJECT/deploy/gstd.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gstd.service
sudo systemctl start gstd.service

echo "Server ECHO-PROJECT Installation"

# Ajout du service python server.py
sudo cp ~/code/ECHO-PROJECT/deploy/mqtt_server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mqtt_server.service
sudo systemctl start mqtt_server.service


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

# installation Docker
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/raspbian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/raspbian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

 sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin


# OPTION INSTALL WITH NVME disk
# Identifier le disque
lsblk

# Création du mount point
sudo mkdir /mnt/NVME

# Formatage du disque
sudo mkfs.ext4 /dev/nvme0n1

# Mounting
sudo mount /dev/nvme0n1 /mnt/NVME

# AUTO Mount
sudo vi /etc/fstab
# Add the following line at the end:
/dev/nvme0n1 /mnt/nvme ext4 defaults 0 2

# unmount ( if necessary )
sudo umount /mnt/NVME
