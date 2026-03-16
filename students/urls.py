from django.urls import path
from .views import *
from .views_reports import *
from .views_admin import *



urlpatterns = [

    path("query_page_list", StudentQuery_list.as_view()),
    path("studentdata_page_list", StudentData_list.as_view()),
    path("studentpayment_page_list", StudentPayment_list.as_view()),
    path("studentefospayment_page_list", StudentEfosPayment_list.as_view()),
    path("studentcampus_page_list", CampusStudent_list.as_view()),
    path('get-student-campus-report-pdf/', GetStudentCampusReportPDFView.as_view(), name="get-student-campus-report-pdf"),
    path('get-student-campus-report-excel/', GetStudentCampusReportExcelView.as_view(), name="get-student-campus-report-excel"),
    path("facultycampus_page_list", CampusFaculty_list.as_view()),
    path('get-faculty-campus-report-pdf/', GetFacultyCampusReportPDFView.as_view(), name="get-faculty-campus-report-pdf"),
    path('get-faculty-campus-report-excel/', GetFacultyCampusReportExcelView.as_view(), name="get-faculty-campus-report-excel"),

    path("automate-email-task", ExportPaymentExcelView.as_view()),

    path("test", GetSessionReportPDFView.as_view()),
    path("test_excel", GetSessionReportExcelView.as_view()),

    path("upload_file", GetSessionFileUploadView.as_view()),

    path("payment_reports_pdf", GetPaymentReportPDFView.as_view()),
    path("payment_report_excel", GetPaymentReportExcelView.as_view()),

    path("campusfaculty_reports_pdf", GetCampusFacultyReportPDFView.as_view()),
    # path("payment_report_excel", GetPaymentReportExcelView.as_view()),

    path('contact-us/', ContactUsView.as_view(), name="contact-us"),
    path('get-contact-us-list/', GetContactUSView.as_view(), name="get-contact-us-list"),
    path('get-contact-us-report-pdf/', GetContactusReportPDFView.as_view(), name="get-contact-us-report-pdf"),
    path('get-contact-us-report-excel/', GetContactusReportExcelView.as_view(), name="get-contact-us-report-excel"),

    path('create-update-student-profile/', CreateStudentProfileView.as_view(), name="create-update-student-profile"),
    path('student-slot-upload/', StudentSlotBookView.as_view(), name="student-slot-upload"),
    path('student-admit-card-download/', GetStudentAdmitCardView.as_view(), name="student-admit-card-download"),
    path('get-student-profile/', GetStudentProfileView.as_view(), name="get-student-profile"),
    path('get-student-profile-listing/', GetStudentProfileListingView.as_view(), name="get-student-profile-listing"),

    path('start_mock_test_status/', StudentMockTestStartStatusView.as_view(), name="start_mock_test_status"),
    path('complete_mock_test_status/', StudentMockTestCompleteStatusView.as_view(), name="complete_mock_test_status"),


    path('update-student-verification-status/', CampusStudentVerifiedStatusView.as_view(), name="update-student-verification-status"),
    path('update-student-mail-status/', CampusStudentAccountMailStatusView.as_view(), name="update-student-mail-status"),
]