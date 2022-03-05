from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate

import copy
from .forms import NewUserForm, Rate
from .models import Movie, Categories, Rating, Rent_Movie_Base, Rent_Status


def index(request):
    obj = Movie.objects.filter().order_by('-pub_date')[:2]
    mov = Movie.objects.all()
    categories = Categories.objects.all()
    movies_name = []
    amount_of_movies = []

    counter = 0
    for x in categories:
        for m in mov:
            if x.category_name not in movies_name:
                movies_name.append(str(x.category_name))
            if str(x.category_name) == str(m.categories):
                counter += 1

        amount_of_movies.append(counter)
        counter = 0

    movies_dict = dict(zip(movies_name, amount_of_movies))
    movies_dict = (dict(sorted(movies_dict.items(), key=lambda x: x[1])))
    it = 0
    new_dict = copy.copy(movies_dict)
    ld = len(movies_dict)
    for x in new_dict:
        if it < (ld-5):
            movies_dict.pop(x)
        it += 1
    l = list(movies_dict.keys())
    l.reverse()
    return render(request, 'index.html', context={
        'movie': obj,
        'cat': l
    })


def reg(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        pass1 = form['password1'].value()
        pass2 = form['password2'].value()
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Created account: {user.username}")
            return redirect('login_request')
        else:
            if pass1 == pass2:
                messages.error(request, "This user already exists!")
            else:
                messages.error(request, "Passwords dont match!")

    form = NewUserForm
    return render(request, 'register.html', context={"form": form})
    pass


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Jestes zalogowany jako: {username}")
                return redirect('index')
            else:
                messages.error(request, "Niepoprawna nazwa uzytkownika lub haslo")
        else:
            messages.error(request, "Niepoprawna nazwa uzytkownika lub haslo")

    form = AuthenticationForm()
    return render(request, 'login.html', context={"form": form})
    pass


def logout_request(request):
    logout(request)
    messages.info(request, "Wylogowano")
    return redirect('index')
    pass


def movie_list(request, slug):
    current_user = request.user
    # check which movies are rented by current user
    def check_movies_rented_by_user():
        for m in movies_list:
            rent_movie_list = Rent_Movie_Base.objects.filter(movie_slug=m, user_id=current_user.id)
            if rent_movie_list.exists():
                rented_movies_binary.append(1)
            else:
                rented_movies_binary.append(0)

    if current_user != None:
        current_user = request.user
        rented_movies_binary = []
        if slug == "all":
            movies_list = Movie.objects.all()
            check_movies_rented_by_user()
        elif slug == "search":
            query = request.GET.get('movie_search')
            if query == None or query == "":
                movies_list = Movie.objects.all()
                check_movies_rented_by_user()
            else:
                movies_list = Movie.objects.filter(name__icontains=query)
                check_movies_rented_by_user()
                categories = Categories.objects.all()
                return render(request, 'movies.html', {
                    'mov': movies_list,
                    'cat': categories})
        else:
            category_obj = Categories.objects.filter(slug=slug)
            category_id = Categories.objects.get(category_name=category_obj[0])
            movies_list = Movie.objects.filter(categories=category_id)
            check_movies_rented_by_user()

        categories = Categories.objects.all()
        paginator = Paginator(movies_list, 3)
        page = request.GET.get('page')
        movies_list = paginator.get_page(page)
        return render(request, 'movies.html', {
            'mov': movies_list,
            'cat': categories,
            'rmb': rented_movies_binary
        })
    else:
        if slug == "all":
            movies_list = Movie.objects.all()
        elif slug == "search":
            query = request.GET.get('movie_search')
            if query == None or query == "":
                movies_list = Movie.objects.all()
            else:
                movies_list = Movie.objects.filter(name__icontains=query)
                categories = Categories.objects.all()
                return render(request, 'movies.html', {
                    'mov': movies_list,
                    'cat': categories})
        else:
            category_obj = Categories.objects.filter(slug=slug)
            category_id = Categories.objects.get(category_name = category_obj[0])
            movies_list = Movie.objects.filter(categories=category_id)

        categories = Categories.objects.all()
        paginator = Paginator(movies_list, 3)
        page = request.GET.get('page')
        movies_list = paginator.get_page(page)
        return render(request, 'movies.html', {
            'mov': movies_list,
            'cat': categories})

def all_movies(request):
    current_user = request.user
    rented_movies_binary = []
    # check which movies are rented by current user
    def check_movies_rented_by_user():
        for m in movies_list:
            rent_movie_list = Rent_Movie_Base.objects.filter(movie_slug=m, user_id=current_user.id)
            if rent_movie_list.exists():
                rented_movies_binary.append(1)
            else:
                rented_movies_binary.append(0)

    movies_list = Movie.objects.all()

    if current_user != None:
        check_movies_rented_by_user()

    paginator = Paginator(movies_list, 3)
    movies_list = Movie.objects.all()
    page = request.GET.get('page')
    movies_list = paginator.get_page(page)
    return render(request, 'movies.html', {
        'mov': movies_list,
        'rmb': rented_movies_binary
    })

@login_required()
def rate_movie(request, slug):
    return render(request, "rate_movie.html", {
        'slug' : slug
    })

@login_required()
def rate_movie_post(request, slug):
    if request.method == "POST":
        form = Rate(request.POST)
        if form.is_valid():
            data = form.cleaned_data.get("rate_value")
            movie = get_object_or_404(Movie, slug=slug)
            rating_check = Rating.objects.filter(user_rate=request.user, movie_rate=movie)
            if rating_check.exists():
                Rating.objects.filter(user_rate=request.user, movie_rate=movie).update(rate=data)
            else:
                rating = Rating.objects.create(user_rate=request.user, movie_rate=movie, rate=data)
                rating.save()
            return redirect('index')


def movie_detail(request, slug):
    try:
        movies_detail = Movie.objects.get(slug=slug)
        if movies_detail.type == 'Series':
            number_of_seasons = int(movies_detail.number_of_seasons)
            episodes_per_season = movies_detail.episodes_per_season.split(',')
            return render(request, 'movies_detail.html', {
                'movies_detail': movies_detail,
                'nos' : number_of_seasons,
                'eps' : episodes_per_season
            })
        else:
            return render(request, 'movies_detail.html', {'movies_detail': movies_detail})
    except Movie.DoesNotExist:
        raise Http404("Nie ma takiego filmu")


@login_required()
def rent_movie(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    rent_mov = Rent_Movie_Base.objects.filter(user_id=request.user, movie_slug=movie)
    if rent_mov.exists():
        messages.error(request, f"This {movie.type} already have been rented")
        return redirect("all_movies")
    else:
        rmb_objc = Rent_Movie_Base.objects.create(user_id=request.user, movie_slug=movie)
        Rent_Status.objects.create(rent_movie=rmb_objc)
        number_of_copies = movie.numer_of_copies
        Movie.objects.filter(slug=slug).update(numer_of_copies= number_of_copies - 1)
        messages.success(request, f"Rented {movie.type}:{movie.name}")
        return redirect("all_movies")


@login_required()
def list_of_movies(request):
    try:
        rmb = Rent_Movie_Base.objects.filter(user_id=request.user)
        list_of_rent_movies = []
        slugs = []
        for a in range(0, len(rmb)):
            rent_movie_base_filter = Rent_Movie_Base.objects.filter(user_id=request.user)[a]
            get_movie_object = Movie.objects.get(name=rent_movie_base_filter)
            slugs.append(get_movie_object.slug)
            list_of_rent_movies.append(Rent_Status.objects.filter(rent_movie=rmb[a]))
    except:
        return render(request, 'user_rent_movies.html', {
            'rs': ''
        })
    else:
        return render(request, 'user_rent_movies.html', {
        'rs': list_of_rent_movies,
        'slugs' : slugs
    })

def categories_search(request):
    try:
        cat = Categories.objects.all()
        mov = Movie.objects.all()
        amount_of_movies = []
        counter = 0
        for x in cat:
            for m in mov:
                if str(x.category_name) == str(m.categories):
                    counter += 1

            amount_of_movies.append(counter)
            counter = 0

    except:
        return render(request, 'categories.html', {
            'rs': cat
        })
    else:
        return render(request, 'categories.html', {
            'rs': cat,
            'am' : amount_of_movies
        })


