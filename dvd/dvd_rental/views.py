from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate

from .forms import NewUserForm, Rate
from .models import Movie, Categories, Rating, Rent_Movie_Base, Rent_Status


def index(request):
    obj = Movie.objects.filter().order_by('-pub_date')[0:2]
    categories = Categories.objects.all()
    return render(request, 'index.html', context={
        'movie': obj,
        'cat': categories
    })


def reg(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login_request')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{form.error_messages[msg]}")

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
    all_movies_list = Movie.objects.all()
    return render(request, 'all_movies.html', {
        'mov': all_movies_list })

@login_required()
def rate_movie(request, slug):
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


@login_required()
def movie_detail(request, slug):
    try:
        movies_detail = Movie.objects.get(slug=slug)
    except Movie.DoesNotExist:
        raise Http404("Nie ma takiego filmu")
    return render(request, 'movies_detail.html', {'movies_detail': movies_detail})
    pass


@login_required()
def rent_movie(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    rent_mov = Rent_Movie_Base.objects.filter(user_id=request.user, movie_slug=movie)
    if rent_mov.exists():
        messages.error(request, "Juz wypozyczyles ten film")
    else:
        rmb_objc = Rent_Movie_Base.objects.create(user_id=request.user, movie_slug=movie)
        Rent_Status.objects.create(rent_movie=rmb_objc)
        number_of_copies = movie.numer_of_copies
        Movie.objects.filter(slug=slug).update(numer_of_copies= number_of_copies - 1)
        messages.success(request, "Wypozyczono film")
    return redirect("/movies")


@login_required()
def list_of_movies(request):
    rmb = Rent_Movie_Base.objects.filter(user_id=request.user)[0]
    rs = Rent_Status.objects.filter(rent_movie = rmb)
    return render(request, 'user_rent_movies.html', {
        'rs': rs
    })


