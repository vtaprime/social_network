# Python entry task deploy guideline

##Install python 2.7
```commandline
sudo apt update
sudo apt install python2.7 python-pip
```
## Install require packages
```commandline
sudo -s        # Be the super user
apt-get update
apt-get install nginx mysql-server python-pip python-dev libmysqlclient-dev ufw
```
Now, the virtualenv and MySQL packages from python repository. 
```commandline
pip install virtualenv MySQL-python
```
## Create and import database
```commandline
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password'; #change password of root
FLUSH PRIVILEGES;

```
```buildoutcfg
'DATABASE NAME': 'social_sharing',
'USER': 'root',
'PASSWORD': '12345678'
```
## Application environment
```commandline
cd /path/social_network  # path of source
pip install virtualenv
virtualenv ~/venv    # Virtual Environment
source ~/venv/bin/activate     # Activate it
cd social_sharing
pip install requirements.txt  # Install python-lib need for app
python manage.py syncdb

```
## Create systemd daemon process
```commandline
sudo nano /etc/systemd/system/gunicorn.service

```
After that, write this configuration and save the service file 
```text
[Unit]
Description=gunicorn service
After=network.target

[Service]
User='your-username'
Group=www-data
WorkingDirectory=/home/'your-username'/path-to/social_network/social_sharing
ExecStart=/home/'your-username'/path-to/social_network/venv/bin/gunicorn --access-logfile - --workers 3 --chdir /home/'your-username'/path-to/social_network/social_sharing/ --bind unix:/home/'your-username'/path-to/social_network/social_sharing/social_sharing.sock social_sharing.wsgi:application

[Install]
WantedBy=multi-user.target

```
Save the file and start gunicorn service
```commandline
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```
## NGINX server
Create a new project file for nginx server under sites-available directory. This would define how the server will respond to a client request. 
```commandline
sudo nano /etc/nginx/sites-available/social_sharing
```
Defind a server
```text
server {
       listen 80;
       server_name localhost;
       location = /favicon.ico {access_log off;log_not_found off;}

       location /static/ {
            root /home/'your-username'/path-to/social_network/social_sharing;
       }

       location /media/ {
            root /home/'your-username'/path-to/social_network/social_sharing;
       }

       location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header X-Forwarded-Host $server_name;
            proxy_set_header X-Real-IP $remote_addr;
            add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
       }

```
## Server completion
Enable the site project by creating its link in the enabled sites directory, located under nginx config directory. 
```commandline
ln -s /etc/nginx/sites-available/social_sharing /etc/nginx/sites-enabled/social_sharing
```
Allow the firewall to pass traffic through port 80
```commandline
ufw allow 'Nginx Full'
```
Restart nginx and gunicorn services and test your site again. 
```commandline
systemctl restart gunicorn
systemctl restart nginx
```