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


# echo "######### Installation NodeJS"
# sudo apt install -y ca-certificates curl gnupg
# curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/nodesource.gpg
# NODE_MAJOR=22
# echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
# sudo apt update
# sudo apt install nodejs
# node -v

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
sudo cp ~/ECHO-PROJECT/deploy/gstd.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gtsd.service
sudo systemctl start gtsd.service

echo "Server ECHO-PROJECT Installation"

