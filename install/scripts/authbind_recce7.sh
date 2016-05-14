#!/bin/sh

if which authbind > /dev/null; then
    sudo authbind recce7.sh
else
    echo "You don't seem to have authbind installed. Authbind is only available"
    echo "for Linux, and must be compiled from scratch in Cent OS. In Debian, you"
    echo "may install authbind by running"
    echo
    echo "    sudo apt-get install authbind"
    echo
    while true; do
        read -p "Do you want to install authbind now? " yn
        case $yn in
            [Yy]* ) sudo apt-get install authbind; sudo authbind recce7.sh; break;;
            [NN]* ) exit;;
            * ) echo "Please answer yes or no"
        esac
    done
fi