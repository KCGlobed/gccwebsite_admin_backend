from django.urls import path
from .views import *

urlpatterns = [

    path("careerapplication_page_list", CareerApplication_list.as_view()),
    path("partners_page_list", PartnerWithUs_list.as_view()),

    path("createdossierform", DossierDataForm_Create.as_view()),
    path("createdossiercustomform", DossierDataFormCustom_Create.as_view()),
    path("createdossierdocument", DossierDocument_Create.as_view()),
    path("createabondantform", DossierAbondant_Create.as_view()),
    path("createvslform", VslDataForm_Create.as_view()),
    path("createvslfinalform", VslFinalDataForm_Create.as_view()),
    path("createvsldetailform", VslOptinDetailDataForm_Create.as_view()),

    path("addvsldetailform", VslOptinDetailDataForm_Update.as_view()),
    path("vsladvisor_page_list", VSLAdvisorDataForm_List.as_view()),

    path("dossierdata_page_list", DossierDataForm_List.as_view()),
    path("abondantdata_page_list", AbondantDataForm_List.as_view()),
    path("dossiersourcedata_page_list", DossierDataSourceForm_List.as_view()),
    
    path("newslettersubscribers_page_list", NewsletterSubscribers_List.as_view()),

    path("createsupportform", CreateSupportFormView.as_view()),
    path("supportform_page_list", SupportForm_page_list.as_view()),

    path('get-dossier-report-pdf/', GetDossierReportPDFView.as_view(), name="get-dossier-report-pdf"),
    path('get-dossier-report-excel/', GetDossierReportExcelView.as_view(), name="get-dossier-report-excel"),

    path('get-dossier-report-excel-six/', GetDossierAffliateSixReportExcelView.as_view(), name="get-dossier-report-excel-six"),

    path('get-dossier-source-report-pdf/', GetDossierSourceReportPDFView.as_view(), name="get-dossier-source-report-pdf"),
    path('get-dossier-source-report-excel/', GetDossierSourceReportExcelView.as_view(), name="get-dossier-source-report-excel"),

    path('get-dossier-vsl-source-report-pdf/', GetDossierVSLSourceReportPDFView.as_view(), name="get-dossier-vsl-source-report-pdf"),
    path('get-dossier-vsl-source-report-excel/', GetDossierVSLSourceReportExcelView.as_view(), name="get-dossier-vsl-source-report-excel"),  ##last update -  not working in admin


    path('get-amendment-source-report-excel/', GetAmendmentSourceReportExcelView.as_view(), name="get-dossier-source-report-excel"),

    path("get-vsl-advisor-report-excel/", GetVSLAdvisorReportExcelView.as_view()),
    path("get-vsl-advisor-report-pdf/", GetVSLAdvisorReportPDFView.as_view()),

    ## Delete data

    path("delete_lead", GetDeleteLead.as_view()),
    path("meritto_lead_push_refresh", DossierMeritto_CreateUpdate.as_view()),
    path("meritto_lead_excel_match", ExcelPhoneMatchAPI.as_view()),
    path("excel_file_create", ExcelLogicProcessAPI.as_view()),


    ### test ###
    path("excel_import", ImportEmailView.as_view()),
    path("add_lead", GetAffliateSixExcelView.as_view()),

    path("af_download_excel", GetAffliateSevenLeadAllReportExcelView.as_view()),

    path("interview_affliateseven_page_list/", InterviewSlotScheduleAdmin_list.as_view(), name="interview_listing_affliateseven"),
    path("interview_affliateseven_report-excel/", GetDossierInterviewAffliateSevenReportExcelView.as_view(), name="interview_affliateseven_report_excel"),
    
    # path("get-dossier-time-slot/", DossierTimeSlotAPIView.as_view()),

]

