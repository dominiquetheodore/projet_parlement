# nosdeputes.mu
## Overview
Code repository for nosdeputes.mu project, a parliament monitoring website for the National Assembly of Mauritius. Scrapes publicly available Hansards to build a database of PQs, PNQs and measure the performance of our Honorable MPs.

## Requirements
### VirtualBox
To run the project, you must have VirtualBox installed on your computer. Download the platform package for your operating system [here](https://www.virtualbox.org/wiki/Downloads)

### Vagrant
To run the project,you will need to download a pre-configured Vagrant VM. This will allow you to share files between the VM and your host computer. Download the Vagrantfile [here](https://www.dropbox.com/s/i8dr95ualpwf1wj/Vagrantfile?dl=0)


## Usage
To convert new Hansards to txt, place the pdf files in the pdf folder of the project, and run:

``` python importdb.py ```

To rebuild the database:

```./init.sh ```

To update the database:

```./update.sh ```

To run the project:

- Start and connect to the Vagrant VM:

```
vagrant up
vagrant ssh
```

- Run ```python project.py``` from the Vagrant machine

- Visit http://localhost:5000/