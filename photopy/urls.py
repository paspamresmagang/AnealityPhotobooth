from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import apply_mass_filter


urlpatterns = [
    path('', views.home, name='home'),
    path('aneality/', views.show_aneality),
    path('camera-shoot/', views.navtocamera, name="navtocamera"),
    path('camera-shoot/result/', views.navtoresult, name="navtoresult"),
    path('save-photos/', views.save_photos, name='save_photos'),
    path('retake/', views.retake_photos, name='retake_photos'),
    path('apply-mass-filter/', apply_mass_filter, name='apply_mass_filter'),
    path('apply-frame/', views.apply_frame, name='apply_frame'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
