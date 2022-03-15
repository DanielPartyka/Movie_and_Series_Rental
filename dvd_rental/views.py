from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.core.mail import EmailMessage
import copy

from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import NewUserForm, Rate, CaptchaTestForm
from .models import Movie, Categories, Rating, Rent_Movie_Base, Rent_Status, Messages
from .token import account_activation_token


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
    image_src = []
    for i in range (0, len(l)):
        categories_obj = Categories.objects.get(category_name=l[i])
        image_src.append(categories_obj.src)
    return render(request, 'index.html', context={
        'movie': obj,
        'cat': l,
        'imsrc' : image_src
    })

def navigator_search(request):
    query = request.GET.get('search')
    get_categories = Categories.objects.filter(category_name__icontains=query)
    get_movies = Movie.objects.filter(name__icontains=query)
    matches_found = int(len(get_categories)) + int(len(get_movies))
    return render(request, 'navigator_search.html', {
        'cat' : get_categories,
        'mov' : get_movies,
        'mat' : matches_found
    })

@login_required()
def send_message(request):
    if request.POST:
        form = CaptchaTestForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            text = form.cleaned_data.get('text')
            human = True
            m = Messages(user_id=request.user, subject=subject, text=text)
            m.save()
            messages.success(request, "Message has been sent")
            form = CaptchaTestForm()
    else:
        form = CaptchaTestForm()
    return render(request, 'contact.html', {'form': form})

def reg(request):
    # iterate after form error object
    def get_error_message(form_field):
        if form_field in errors:
            error_list_length = len(errors[form_field])
            if error_list_length < 2:
                x = errors[form_field][0]
                for a in x:
                    messages.error(request, a)
            else:
                for i in range(0, error_list_length):
                    x = errors[form_field][i]
                    for a in x:
                        messages.error(request, a)

    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active  = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, f"Created account: {user.username}")
            return render(request, 'email_confirmation.html')
            # messages.success(request, f"Created account: {user.username}")
            # return redirect('login_request')
        else:
            errors = form.errors.as_data()
            username = 'username'
            password = 'password2'
            if username in errors:
                get_error_message(username)
            if password in errors:
                get_error_message(password)

    form = NewUserForm
    return render(request, 'register.html', context={"form": form})
    pass

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f"Account activated")
        return redirect('login_request')
    else:
        return HttpResponse('Activation link is invalid!')

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
    categories = Categories.objects.all()
    movies_list = paginator.get_page(page)
    return render(request, 'movies.html', {
        'mov': movies_list,
        'cat': categories,
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
            messages.success(request,"Rating updated!")
            return redirect('movies_rent_by_user')


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
        messages.success(request, f"Rented {movie.type}: {movie.name}")
        return redirect("all_movies")


@login_required()
def list_of_movies(request):
    try:
        rmb = Rent_Movie_Base.objects.filter(user_id=request.user)
        list_of_rent_movies = []
        slugs = []
        # Boolean values
        is_rated = []
        for a in range(0, len(rmb)):
            rent_movie_base_filter = Rent_Movie_Base.objects.filter(user_id=request.user)[a]
            get_movie_object = Movie.objects.get(name=rent_movie_base_filter)
            slugs.append(get_movie_object.slug)
            rating_obj = Rating.objects.filter(movie_rate=get_movie_object)
            if rating_obj.exists():
                get_rating_obj = Rating.objects.get(movie_rate=get_movie_object)
                is_rated.append(get_rating_obj.rate)
            else: is_rated.append(0)
            list_of_rent_movies.append(Rent_Status.objects.filter(rent_movie=rmb[a]))
    except:
        return render(request, 'user_rent_movies.html', {
            'rs': ''
        })
    else:
        return render(request, 'user_rent_movies.html', {
        'rs': list_of_rent_movies,
        'slugs' : slugs,
        'rate' : is_rated
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


