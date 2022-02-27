import datetime

from django.contrib import admin
from django.shortcuts import get_object_or_404

from .models import Movie, Categories, Rent_Movie_Base, Rating, Rent_Status

def change_status_Confirmed(modeladmin, request, queryset):
    queryset.update(rent_status = 'Confirmed')

def change_status_Awaiting_to_pick_up(modeladmin, request, queryset):
    queryset.update(rent_status = 'Awaiting to pickup')

def change_status_Rented(modeladmin, request, queryset):
    # today date
    today = datetime.date.today()
    # 7 days after
    date = today + datetime.timedelta(7)
    queryset.update(rent_status = 'Rented', rent_date = today, return_date = date)


def change_status_Returned(modeladmin, request, queryset):
    queryset.update(rent_status='Returned')

    def get_value_from_queryset(parameter, obj):
        for item in obj.values_list(parameter, flat=True):
            x = item
        return x
    rent_movie_id = 0
    for item in queryset.values_list('rent_movie', flat=True):
        rent_movie_id = item
        print(item)
    for item in queryset.values_list('rent_uid', flat=True):
        print('user_id: ',item)
    movie_name = Rent_Movie_Base.objects.filter(rent_id=rent_movie_id)
    m = 0
    for item in movie_name.values_list('movie_slug', flat=True):
        m = item
    for item in movie_name.values_list('user_id', flat=True):
        print('user_id: ',item)
    x = Movie.objects.filter(id=m)
    x1 = Movie.objects.get(id=m)
    Movie.objects.filter(id=m).update(numer_of_copies=x1.numer_of_copies + 1)
    name = get_value_from_queryset('name', x)
    print(name)


change_status_Rented.short_description = 'Change Status to rented'
change_status_Returned.short_description = 'Change Status to returned'

class Rent_StatusA(admin.ModelAdmin):
      actions = [change_status_Rented, change_status_Returned, change_status_Confirmed, change_status_Awaiting_to_pick_up]

admin.site.register(Movie)
admin.site.register(Categories)
admin.site.register(Rent_Movie_Base)
admin.site.register(Rating)
admin.site.register(Rent_Status, Rent_StatusA)


