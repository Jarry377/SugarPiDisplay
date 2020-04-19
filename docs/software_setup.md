
## Software Setup

### Install Raspian OS
Flash the microSD with Raspian-Lite


### Configuring Raspberry Pi
- ``sudo apt-get update && sudo apt-get upgrade``
- ``sudo raspi-config``
  - configure wifi (including country)
  - enable ssh   # this is optional
  - enable SPI   # needed for e-paper display only
  - set localization (timezone, language, keyboard.  The default GB keyboard layout will be a problem if your wifi password has any symbols)

After Wifi and SSH are configured, you can reboot and connect to it using SSH for the rest of the setup. 

### Installing Dependencies
- ``sudo apt-get install python3-pip``
- ``sudo apt-get install python3-smbus``
- ``sudo apt-get install git``
- ``pip3 install RPi.GPIO``
- ``pip3 install spidev``
- ``pip3 install Pillow``


### Installing SugarPiDisplay

- ``git clone https://github.com/bassettb/SugarPiDisplay.git``
- ``pip3 install SugarPiDisplay/``
- ``chmod 755 SugarPiDisplay/install.sh``
- ``SugarPiDisplay/install.sh``
- reboot the Raspberry Pi and SugarPiDisplay should be running


### Configuring SugarPiDisplay

- Once SugarPiDisplay is running, you can configure it using its web interface on port 8080.  It will display its IP address for several seconds during startup.  Enter this IP into your browser with ":8080" on the end and you'll see the config screen.  From here you can pick Dexcom or Nightscout and enter in the necessary fields.   
- Nightscout token: If you will be getting your CGM data from nightscout, you'll have to set up a "user" in nightscout.  Under the Admin Tools screen, click the "Add new Subject" button.  Give it a name like SugarPi.  For role, use the "readable" role.  Click Save.  In the list of subjects, your new role will be listed with a generated access token (something like "sugarpi-8c8766b098a988f".  That token is entered under "Nightscout Access Token" in the SugarPiDisplay config.  Note: this requires Nightscout version 0.9 or later.
