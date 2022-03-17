from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('dvd_rental.urls')),
    path('captcha/', include('captcha.urls')),
]

handler404 = 'dvd_rental.views.custom_error_404'