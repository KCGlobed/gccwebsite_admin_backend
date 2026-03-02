from django.urls import path
from .views import *
from .views_reports import *

urlpatterns = [

    path("query_page_list", StudentQuery_list.as_view()),
    path("studentdata_page_list", StudentData_list.as_view()),
    path("studentpayment_page_list", StudentPayment_list.as_view()),
    path("studentcampus_page_list", CampusStudent_list.as_view()),
    path("facultycampus_page_list", CampusFaculty_list.as_view()),


    path("test", GetSessionReportPDFView.as_view()),
    path("test_excel", GetSessionReportExcelView.as_view()),

    path("upload_file", GetSessionFileUploadView.as_view()),

    path("payment_reports_pdf", GetPaymentReportPDFView.as_view()),
    path("payment_report_excel", GetPaymentReportExcelView.as_view()),
]