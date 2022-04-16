# Movie_and_Series_Rental
#### Basic website created with Django and Bootstrap4.

![alt text](dvd_rental.png) 
### photo
#### demo: https://dvdrentaldanielpartyka.herokuapp.com/

### Functionalities:
* registration/login (email confirmation)
* simulation of reservation store via wesbite (reservation->confirmation->rental->return)
* filtrating movies and series by name and their categories
* rating in scale (0-5) movie/series
* contact form (secured by captcha)

### Instalation guide:
### required python version 3.8+

## Instalation:
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






