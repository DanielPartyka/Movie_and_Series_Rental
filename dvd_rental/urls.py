from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.reg, name="register"),
    path('login/', views.login_request, name="login_request"),
    path('logout/', views.logout_request, name='user_logout'),
    path('captcha_test/', views.captcha_test, name='captcha_test'),
    path('', views.index, name='index'),
    path('movies/', views.all_movies, name='all_movies'),
    path('movies/<slug>', views.movie_list, name='movie_list'),
    path('movies_detail/<slug>/', views.movie_detail, name="movie_detail"),
    path('add_to_cart/<slug>/', views.rent_movie, name="rent_movie"),
    path('user_rent_movies/', views.list_of_movies, name="movies_rent_by_user"),
    path('user_rent_movies/rate_movie/<slug>/', views.rate_movie, name="rate_movie"),
    path('user_rent_movies/rate_movie/<slug>/rate/', views.rate_movie_post, name="rate_movie_post"),
    path('categories/', views.categories_search, name="categories_search")
]