# E-Commerce
#Execute inside postgresql to create database:
---------------------------------------------------------------------------------
DROP DATABASE IF EXISTS ecommerce;
DROP USER IF EXISTS ecommerceuser;
CREATE DATABASE ecommerce;
CREATE USER ecommerceuser WITH PASSWORD 'password';
ALTER ROLE ecommerceuser SET client_encoding TO 'utf8';
ALTER DATABASE ecommerce SET timezone TO 'Asia/Kolkata';
ALTER ROLE ecommerceuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE ecommerceuser SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE ecommerce TO ecommerceuser;
\c ecommerce
GRANT CREATE ON SCHEMA public TO ecommerceuser;


#Create virtual environment and activate it:
---------------------------------------------------------------------------------
python3 -m venv virtual-env

source virtual-env/bin/activate

pip install -r requirements.txt


#Create django project:
---------------------------------------------------------------------------------
django-admin startproject ecommerce


#Create django app:
---------------------------------------------------------------------------------
python manage.py startapp accounts

python manage.py startapp shopping


---------------------------------------------------------------------------------
for x in accounts shopping system; do rm -rf $x/migrations; mkdir $x/migrations; touch $x/migrations/__init__.py; done

python manage.py create_ecommerce_setup

python manage.py runserver


---------------------------------------------------------------------------------

