import secrets
from enum import Enum
from django.conf import settings
from django.db import models
from autoslug import AutoSlugField
from django.core.validators import MaxValueValidator, MinValueValidator

class Name(models.CharField):
    def __init__(self, *args, **kwargs):
        super(Name, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower()

class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    src = models.CharField(max_length=130, default='give_image_source')
    category_name = Name(max_length=130,blank=False)
    slug = AutoSlugField(populate_from='category_name')

    def __str__(self):
        return self.category_name

class Movie(models.Model):
    class Movie_or_Series(Enum):
        mov = ('Movie', 'Movie')
        ser = ('Series', 'Series')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    name = models.CharField(max_length=130)
    slug = AutoSlugField(populate_from='name')
    src = models.CharField(max_length=130)
    pub_date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=250)
    price = models.CharField(max_length=130)
    type = models.CharField(blank=False, choices=[x.value for x in Movie_or_Series], max_length=30)
    movie_length = models.CharField(max_length=130, blank=True, null=True)
    number_of_seasons = models.IntegerField(null=True, blank=True)
    episodes_per_season = models.CharField(max_length=130, blank=True, help_text='Please use this format: number_of_eps_'
                                                                                 'in_season_x, number_of_eps_'
                                                                                 'in_season_x+1, etc')
    categories = models.ForeignKey(Categories,on_delete=models.CASCADE)
    numer_of_copies = models.IntegerField(validators=[MinValueValidator(0)], blank=False, default=1)

    def __str__(self):
        return self.name

    def check_movie_renting(self):
        rent_movie = Rent_Movie_Base.objects.filter(movie_slug=self)
        count = len(rent_movie)
        if count == 0 or count == None:
            return True
        else:
            return False

    def get_avg_rating(self):
        rating_movies = Rating.objects.filter(movie_rate=self)
        count = len(rating_movies)
        sum = 0
        if count == 0:
            return 0
        else :
            for rvw in rating_movies:
                sum += rvw.rate
            return float(sum/count)


    def rating_count(self):
        rating_movies = Rating.objects.filter(movie_rate=self)
        return len(rating_movies)

    def __str__(self):
        return self.name

class Rent_Movie_Base(models.Model):
    rent_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    movie_slug = models.ForeignKey(Movie,on_delete=models.CASCADE)

    def __str__(self):
        return self.movie_slug.name

class Rent_Status(models.Model):
    class Status(Enum):
        acc = ('Accepted', 'Accepted')
        con = ('Confirmed', 'Confirmed')
        aop = ('Awaiting to pickup', 'Awaiting to pickup')
        ren = ('Rented', 'Rented')
        ret = ('Returned', 'Returned')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    rent_status_id = models.AutoField(primary_key=True)
    rent_movie = models.ForeignKey(Rent_Movie_Base, on_delete=models.CASCADE)
    rent_uid = models.IntegerField(default=(secrets.SystemRandom().randrange(100000, 999999)))
    rent_status = models.CharField(default='Accepted', choices=[x.value for x in Status], max_length=30)
    rent_date = models.DateField(default=None, null=True)
    return_date = models.DateField(default=None, null=True)

    def __str__(self):
        return "{rent_uid}".format(rent_uid=self.rent_uid)

class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    user_rate = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    rate = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    movie_rate = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return self.movie_rate.name + ': ' + str(self.rate)

class Messages(models.Model):
    message_id = models.AutoField(primary_key = True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=130)
    text = models.CharField(max_length=400)

    def __str__(self):
        return self.subject



