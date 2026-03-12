from django.urls import path
from .views import *

urlpatterns = [

    path("careerapplication_page_list", CareerApplication_list.as_view()),
    path("partners_page_list", PartnerWithUs_list.as_view()),

    path("createdossierform", DossierDataForm_Create.as_view()),
    path("dossierdata_page_list", DossierDataForm_List.as_view()),
    
    path("newslettersubscribers_page_list", NewsletterSubscribers_List.as_view()),

    path("createsupportform", CreateSupportFormView.as_view()),
    path("supportform_page_list", SupportForm_list.as_view()),

    path('get-dossier-report-pdf/', GetDossierReportPDFView.as_view(), name="get-dossier-report-pdf"),
    path('get-dossier-report-excel/', GetDossierReportExcelView.as_view(), name="get-dossier-report-pdf"),
]