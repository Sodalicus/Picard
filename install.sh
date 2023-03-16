#! /bin/bash
#
# install.sh
# Copyright (C) 2022 Paweł Krzemiński 
#
# Distributed under terms of the MIT license.
#

#echo "This install script will try to copy and setup right ownership of project files."
#echo "Setup systemd services"
#echo "In the futute maybe take care of requirements"

shopt -s extglob # sets extended pattern matching options in the bash shell

installPath="/var/lib/www/picard/"
logPath="/var/log/uwsgi"
pidFilePath="/run/uwsgi"
userName="picard"

#groups=("dialout","input","audio","spi") 

# 1. Are you running the script as a root
# 1a. Are old services running? if so, stop them
# 2. Does the user picard exists, if not create it
# 3. Add user picard to required groups.
# 4. Create directories, and set right ownership
#  - app directory /var/lib/www/picard 
#  - log directory /var/log/uwsgi
#  - pid file directory /run/uwsgi
# 5. Copy files
#  - all files to app directory
#    * ask if overwrite
#    * ask if overwrite database file separately
#  - create log file in /var/log/uwsgi/uwsgi.log
#  - copy .service files to /etc/systemd/system
# 6. systemctl daemon-reload
# 7. check for and install required libraries and packages
# 8. setup system requiments
#  - irda setup
#  - seven segment display setup
# 


# 1. Are you running the script as a root
if [ $(id -u) -ne 0 ]; then
    echo "You're not root"
    #exit 1
fi

# 1a. Are old services running? if so, stop them
if [ $(systemctl -is-active --quiet picard_main.service) -eq 0 ] || [ $(systemctl -is-active --quiet picard_uwsgi.service) -eq 0 ]; then
    echo "One or both picard services are running, if you want to continue, you have to stop them"
    read -n 1 -r -p "Do you want to stop the services?"
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping service  picard_main.service"
        systemctl stop picard_main.service
        echo "Stopping service picard_uwsgi.service"
        systemctl stop picard_uwsgi.service
    else
        echo "Quiting.."
        exit 1
    fi
fi


# 2. Does the user picard exists, if not create it
#if id ${userName} 2>/dev/null; then  
#    echo "user found"
#else
#    echo "user www-picard doesn't exist, creating it."
#    useradd -UM -s /usr/sbin/nologin -d ${installPath} ${userName} 
#fi

# 3. Add user picard to required groups.
#usermod -aG dialout,input,audio,spi picard


# 4. Create directories, and set right ownership
#  - app directory /var/lib/www/picard 
#mkdir -p ${installPath} 
#chown ${userName}:${userName} ${installPath} 

#  - log directory /var/log/uwsgi
#mkdir -p ${logPath}
#chown ${userName}:${userName} ${logPath} 

#  - pid file directory /run/uwsgi
#mkdir -p ${pidFilePath} 
#chown ${userName}:${userName} ${pidFilePath} 


# 5. Copy files
#  - all files to app directory
#if [ -f ${installPath}picard_main.py ]; then

#    read -n 1 -r -p "It seems you have picard already installed, do you want to overwrite the installation?"
#    echo
#    * ask if overwrite
#    if [[ $REPLY =~ ^[Yy]$ ]]; then
#        echo "Coping app files.."
#        cp -r !(base.db | __pycache__ | .git | .gitignore) ${installPath} 
#    else
#        echo "Won't overwrite app files."
#    fi
#else
#    echo "No old installation found, coping app files.."
#    cp -r !(base.db | __pycache__ | .git | .gitignore) ${installPath} 
#fi

# change ownership

#if [ -d ${installPath} ]; then
#    chown -R ${userName}:${userName} ${installPath} 
#fi

    
#    * ask if overwrite database file separately
#if [ -f ${installPath}base.db ]; then
#    read -n 1 -r -p "Do you want to overwrite old database file?"
#    echo
#    if [[ $REPLY =~ ^[Yy]$ ]]; then
#        echo "Overwriting old database."
#        cp ./base.db ${installPath}
#    else
#        echo "Keeping old database"
#    fi
#else
#    echo "No old database found, coping database file."
#    cp ./base.db ${installPath}
#fi

#if [ -f ${installPath}base.db} ]; then
#    chown ${userName}:${userName} ${installPath}base.db
#fi

#  - create log file in /var/log/uwsgi/uwsgi.log
#if [ -f ${logPath}uwsgi.log ]; then
#    echo "kkk"
#fi

#  - copy .service files to /etc/systemd/system
if [ -f /etc/systemd/system/picard_main.service ]; then
    echo "Do you want to overwrite: "
    read -n 1 -r -p  "/etc/systemd/system/picarm_main.service ?"
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Overwriting old picard_main.serice file."
        cp ./picard_main.service /etc/systemd/system/
    else
        echo "Keeping old picard_main.service file."
    fi
else
    echo "Coping picard_main.service file."
    cp ./picard_main.service /etc/systemd/system/
fi


if [ -f /etc/systemd/system/picard_uwsgi.service ]; then
    echo "Do you want to overwrite: "
    read -n 1 -r -p  "/etc/systemd/system/picarm_uwsgi.service ?"
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Overwriting old picard_uwsgi.serice file."
        cp ./uwsgi/picard_uwsgi.service /etc/systemd/system/
    else
        echo "Keeping old picard_uwsgi.service file."
    fi
else
    echo "Coping picard_uwsgi.service file."
    cp ./uwsgi/picard_uwsgi.service /etc/systemd/system/
fi

# upade systemd services
systemctl daemon-reload

exit 0
