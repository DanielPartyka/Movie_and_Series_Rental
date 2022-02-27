from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',views.reg,name="register"),
    path('login/',views.login_request,name="login_request"),
    path('logout/', views.logout_request, name='user_logout'),
    path('', views.index, name='index'),
    path('movies/', views.all_movies, name='movies'),
    path('movies/<slug>', views.movie_list, name='movie_list'),
    path('movies_detail/<slug>/',views.movie_detail,name="movie_detail"),
    path('add_to_cart/<slug>/',views.rent_movie,name="rent_movie"),
    path('movies_rate/<slug>',views.rate_movie,name="rate_movie"),
    path('user_rent_movies/',views.list_of_movies,name="movies_rent_by_user"),
]