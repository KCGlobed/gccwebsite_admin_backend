from django.urls import path
from .views import *

urlpatterns = [

    path("query_page_list", StudentQuery_list.as_view()),
    path("studentdata_page_list", StudentData_list.as_view()),
    path("studentpayment_page_list", StudentPayment_list.as_view()),

]