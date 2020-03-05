ITEM CATALOG PROJECT
Modern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, 
it’s really all just creating, reading, updating and deleting data. In this project, 
you’ll combine your knowledge of building dynamic websites with persistent data storage 
to create a web application that provides a compelling service to your users.

GITTING STARTED
To start on this project, you'll need database software (provided by a Linux virtual machine) and the data to analyze.
and you can use the sqlalchemy database and support software needed to complete this project
and you'll need to use flask library in python.

PREREQUISITES
1) build a database using sqlalchemy
2) use flask library in python 
3) Virtual Box Software.
4) vagrant software.
5) Python 3 
6) connect to database using sqlalchemy library 
7) use HTML templates
8) decorate your website using css

INSTALLING
1) Install VirtualBox Software:
VirtualBox is the software that actually runs the virtual machine.
Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that. Currently (October 2017), the supported version of VirtualBox to install is version 5.1. Newer versions do not work with the current release of Vagrant.

2) Install Vagrant Software:
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.

3) Download the VM configuration:
There are a couple of different ways you can download the VM configuration.
You can download and unzip this file: FSND-Virtual-Machine.zip This will give you a directory called FSND-Virtual-Machine. It may be located inside your Downloads folder.
Alternately, you can use Github to fork and clone the repository https://github.com/udacity/fullstack-nanodegree-vm.
Either way, you will end up with a new directory containing the VM files. 

4) Download python 3 platform

RUNNING THE TESTS:
1) using terminal cd into the project directory.
2) then, cd into vagrant directory.
3) run "vagrant up" then "vagrant ssh" command.
4) run the python file using this command:
vagrant@vagrant:~$ cd /vagrant
vagrant@vagrant:/vagrant/catalog$ python database_setup.py
vagrant@vagrant:/vagrant/catalog$ python database_information.py
vagrant@vagrant:/vagrant/catalog$ python books_application.py


AUTHOR:
Reem Abdulmoti Alsulami - CS Student.

RESOURCES:
https://www.amazon.com/
https://www.pdfdrive.com/
https://github.com/udacity/OAuth2.0