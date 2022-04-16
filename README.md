# Movie_and_Series_Rental
#### Website created with Django and MdBootstrap.
![alt text](dvd_rental.png) 
### demo: https://dvdrentaldanielpartyka.herokuapp.com/

### Technologies:
* Python 3.9.7
* Django 4.0.2
* MdBootstrap 3.10.2

### Functionalities:
* registration/login (email confirmation)
* simulation of reservation store via wesbite (reservation->confirmation->rental->return)
* filtrating movies and series by name and their categories
* rating in scale (0-5) movie/series
* contact form (secured by captcha)

### Instalation guide:
### required python version 3.8+
### Installing dependencies
```
python -m venv venv 
venv\Scripts\activate
pip install -r requirements.txt
```
### Database migration
```
cd dvd_rental
python manage.py makemigrations dvd_rental
python manage.py migrate
```
### Create admin
```
python manage.py createsuperuser
```
### Application running
```
python manage.py runserver
```
### Important







