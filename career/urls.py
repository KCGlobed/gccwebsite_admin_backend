from django.urls import path
from .views import *

urlpatterns = [

    path("careerapplication_page_list", CareerApplication_list.as_view()),
    path("partners_page_list", PartnerWithUs_list.as_view()),

]