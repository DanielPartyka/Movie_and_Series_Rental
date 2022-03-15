from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.reg, name="register"),
    path('activate/?P<uidb64>[0-9A-Za-z_\-]/?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}/',
        views.activate, name='activate'),
    path('login/', views.login_request, name="login_request"),
    path('logout/', views.logout_request, name='user_logout'),
    path('contact/', views.send_message, name='send_message'),
    path('', views.index, name='index'),
    path('search/', views.navigator_search, name='search'),
    path('movies/', views.all_movies, name='all_movies'),
    path('movies/<slug>', views.movie_list, name='movie_list'),
    path('movies_detail/<slug>/', views.movie_detail, name="movie_detail"),
    path('add_to_cart/<slug>/', views.rent_movie, name="rent_movie"),
    path('user_rent_movies/', views.list_of_movies, name="movies_rent_by_user"),
    path('user_rent_movies/rate_movie/<slug>/', views.rate_movie, name="rate_movie"),
    path('user_rent_movies/rate_movie/<slug>/rate/', views.rate_movie_post, name="rate_movie_post"),
    path('categories/', views.categories_search, name="categories_search")
]
