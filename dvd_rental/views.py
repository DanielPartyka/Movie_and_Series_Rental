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

# main page
def index(request):
    # get 2 last added movies
    obj = Movie.objects.filter().order_by('-pub_date')[:2]

    mov = Movie.objects.all()
    categories = Categories.objects.all()
    movies_name = []
    amount_of_movies = []

    # we want to display 5 most popular categories by amount of movies in each category
    counter = 0
    for c in categories:
        for m in mov:
            if c.category_name not in movies_name:
                movies_name.append(str(c.category_name))
            if str(c.category_name) == str(m.categories):
                counter += 1

        amount_of_movies.append(counter)
        counter = 0

    # create a dictionary (movie_name : amount_of_movies)
    movies_dict = dict(zip(movies_name, amount_of_movies))
    # reverse dictionary to make descending order (by amout of movies )
    movies_dict = (dict(sorted(movies_dict.items(), key=lambda x: x[1])))
    it = 0
    new_dict = copy.copy(movies_dict)
    ld = len(movies_dict)

    # get only 5 categories
    for x in new_dict:
        if it < (ld-5):
            movies_dict.pop(x)
        it += 1
    l = list(movies_dict.keys())
    l.reverse()
    image_src = []

    # get image source of each category
    for i in range (0, len(l)):
        categories_obj = Categories.objects.get(category_name=l[i])
        image_src.append(categories_obj.src)

    return render(request, 'index.html', context={
        'movie': obj,
        'cat': l,
        'imsrc' : image_src
    })

# 404 error page
def custom_error_404(request, exception):
    return render(request, '404.html', {})

# navigator search handler
def navigator_search(request):
    query = request.GET.get('search')
    # check if any categorie match with result
    get_categories = Categories.objects.filter(category_name__icontains=query)
    # check if any movie match with result
    get_movies = Movie.objects.filter(name__icontains=query)
    # calculate matches
    matches_found = int(len(get_categories)) + int(len(get_movies))
    return render(request, 'navigator_search.html', {
        'cat' : get_categories,
        'mov' : get_movies,
        'mat' : matches_found
    })

# contact view
@login_required()
def send_message(request):
    if request.POST:
        form = CaptchaTestForm(request.POST)
        if form.is_valid():
            # clear form fields
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

# user registration function
def reg(request):
    # iterate after form error object
    # We want to get error messages from dictionary with certain keys
    def get_error_message(form_field):
        if form_field in errors:
            error_list_length = len(errors[form_field])
            # fields like password can contain multiple errors (more than 1)
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
            # get current URL
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            # in this fragment of code we send an activation mail to the user
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
        else:
            # display username and password errors
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

# user account activation function
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

# log in function
def login_request(request):
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"You are logged as: {username}")
                    return redirect('index')
                else:
                    messages.error(request, "Invalid username or password")
            else:
                messages.error(request, "Invalid username or password")
        form = AuthenticationForm()
        return render(request, 'login.html', context={"form": form})
    except:
        messages.error(request, "Could not create an account")

# logout function
def logout_request(request):
    logout(request)
    messages.info(request, "Log out")
    return redirect('index')

# get movies with certain query
def movie_list(request, slug):
    # get logged user credentials
    current_user = request.user

    # check which movies are rented by current user
    def check_movies_rented_by_user():
        for m in movies_list:
            rent_movie_list = Rent_Movie_Base.objects.filter(movie_slug=m, user_id=current_user.id)
            if rent_movie_list.exists():
                rented_movies_binary.append(1)
            else:
                rented_movies_binary.append(0)

    current_user = request.user
    rented_movies_binary = []
    if slug == "all":
        movies_list = Movie.objects.all()
        if current_user != None:
            check_movies_rented_by_user()
    elif slug == "search":
        query = request.GET.get('movie_search')
        if query == None or query == "":
            movies_list = Movie.objects.all()
            if current_user != None:
                check_movies_rented_by_user()
        else:
            movies_list = Movie.objects.filter(name__icontains=query)
            if current_user != None:
                check_movies_rented_by_user()
            categories = Categories.objects.all()
            return render(request, 'movies.html', {
                'mov': movies_list,
                'cat': categories})
    else:
        category_obj = Categories.objects.filter(slug=slug)
        category_id = Categories.objects.get(category_name=category_obj[0])
        movies_list = Movie.objects.filter(categories=category_id)
        if current_user != None:
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

# get all movies
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
    # if user is not logged in
    if current_user != None:
        check_movies_rented_by_user()

    # create paginator and display only 3 movies on page
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
# go to the rate page
@login_required()
def rate_movie(request, slug):
    return render(request, "rate_movie.html", {
        'slug' : slug
    })
# save user rate
@login_required()
def rate_movie_post(request, slug):
    if request.method == "POST":
        form = Rate(request.POST)
        if form.is_valid():
            data = form.cleaned_data.get("rate_value")
            movie = get_object_or_404(Movie, slug=slug)
            rating_check = Rating.objects.filter(user_rate=request.user, movie_rate=movie)
            # check if user already rated movie
            if rating_check.exists():
                Rating.objects.filter(user_rate=request.user, movie_rate=movie).update(rate=data)
            else:
                rating = Rating.objects.create(user_rate=request.user, movie_rate=movie, rate=data)
                rating.save()
            messages.success(request,"Rating updated!")
            return redirect('movies_rent_by_user')

# movie detail page
def movie_detail(request, slug):
    try:
        movies_detail = Movie.objects.get(slug=slug)
        # movie can be movie and have some length
        # or it could be a series a have seasons with some episodes for each season
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
        raise Http404("There is no such a movie")

# rent movie by user
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

# user list of movies page
@login_required()
def list_of_movies(request):
    try:
        rmb = Rent_Movie_Base.objects.filter(user_id=request.user)
        list_of_rent_movies = []
        slugs = []
        is_rated = []
        # its complicated but we need a 3 lists to display a data
        # in a table from 3 models: Rent_Movie_Base, Movie and Rating
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
# advanced search page
def categories_search(request):
    try:
        cat = Categories.objects.all()
        mov = Movie.objects.all()
        amount_of_movies = []
        counter = 0
        # we calculate how many movies have each category
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


