# FCRM
F+ CRM Project

This is a complete Customer Relation Management for those who use [IBSng Enterprise](https://www.parspooyesh.com/index.php/2017-06-19-19-33-37/mahsoulat-telecom/ibsng-ocs)


### Some of Features:
* IBSng user management
* POP Site/Wireless tower management
* Complete financial system including discount system and virtual banking
* Personnel work time management
* Unlimited user and personnel
* Help Desk
* etc

### Requirements:
This project took about 3 years to complete and Written in Python2.7 and Django 1.6. <br>
Sadly, I have no time to update this to Py3 and django3. <br>
```
Python 2.7
pip install dango==1.6.11
pip install khayyam
pip install celery==3.1.25
pip install django-assets==0.8
pip install cssmin
pip install jsmin
pip install django-audit-log
pip install wand
pip install ago
pip install weasyprint==0.38
pip install ipy
pip install openpyxl
pip install suds
pip install pdfkit
pip install django-redis-cache
pip install redis
```
To install Postgres driver you may need this : 
* sudo apt install libpq-dev

```
pip install psycopg2
```
`This is really important!`

In django V1.6.11, max len of permission model name has been set to 50 chars. This is not enough for CRM.<br>
You may need patch a file in your sites-packages : <br>

`sudo nano /usr/local/lib/python2.7/dist-packages/django/contrib/auth/models.py`

Find perssmion model and change the len of the `name` to `100`! <br>

Clone this project to `/var/CRM/`<br>
Change database username and password in `/var/CRM/settings.py` in `DATABASE` section.<br>
Then run this : 
```
python manage.py syncdb
python manage.py createcachetable crm4
python manage.py createsuperuser
python manage.py shell

from CRM.models import UserProfile
x=UserProfile()
x.user_id=1
x.save()
exit()

python manage.py runserver
```
If things go fine, then server will start and you can access the web interface. <br>
<br>
<br>
# Team Members WERE :( :
* [Samaneh Sobout](https://www.linkedin.com/in/samaneh-sobout-698a8485/)
* [VaheeD Khoshnoud](https://www.linkedin.com/in/vaheed-khoshnoud-81b8811b/)
* [Saeed Jeff](https://github.com/sauditore/)

