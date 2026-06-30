from django.urls import path
from .views import *
from .views_reports import *
from .views_admin import *



urlpatterns = [

    path("query_page_list", StudentQuery_list.as_view()),
    path("studentdata_page_list", StudentData_list.as_view()),
    path("studentpayment_page_list", StudentPayment_list.as_view()),
    path("studentsourcepayment_page_list", StudentSourcePayment_list.as_view()),
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

    path("source_payment_reports_pdf", GetSourcePaymentReportPDFView.as_view()),
    path("source_payment_report_excel", GetSourcePaymentReportExcelView.as_view()),

    path("campusfaculty_reports_pdf", GetCampusFacultyReportPDFView.as_view()),
    # path("payment_report_excel", GetPaymentReportExcelView.as_view()),

    path('contact-us/', ContactUsView.as_view(), name="contact-us"),
    path('get-contact-us-list/', GetContactUSView.as_view(), name="get-contact-us-list"),
    path('get-contact-us-report-pdf/', GetContactusReportPDFView.as_view(), name="get-contact-us-report-pdf"),
    path('get-contact-us-report-excel/', GetContactusReportExcelView.as_view(), name="get-contact-us-report-excel"),

    path('create-update-student-profile/', CreateStudentProfileView.as_view(), name="create-update-student-profile"),
    path('create-student-profile-bot/', CreateStudentProfileByBotView.as_view(), name="create-update-student-profile-bot"),
    path('create-update-student-profile-draft/', CreateStudentProfileDraftView.as_view(), name="create-update-student-profile-draft"),
    path('create-student-interview-slot/', StudentScheduleInterviewView.as_view(), name="create-student-interview-slot"),
    path('create-student-account-interview-slot/', ManageStudentAccountInterviewView.as_view(), name="create-student-account-interview-slot"),
    path('student-slot-upload/', StudentSlotBookView.as_view(), name="student-slot-upload"),
    path('student-admit-card-download/', GetStudentAdmitCardView.as_view(), name="student-admit-card-download"),
    path('student-admit-card-admin-download/<int:id>', GetStudentAdmitCardAdminView.as_view(), name="student-admit-card-admin-download"),
    path('get-student-profile/', GetStudentProfileView.as_view(), name="get-student-profile"),
    path('get-student-profile-draft/', GetStudentProfileDraftView.as_view(), name="get-student-profile-draft"),
    path('exam-re-attempt-status/', GetStudentReAttemptView.as_view(), name="exam-re-attempt-status"),
    path('get-student-profile-listing/', GetStudentProfileListingView.as_view(), name="get-student-profile-listing"),

    path('start_mock_test_status/', StudentMockTestStartStatusView.as_view(), name="start_mock_test_status"),
    path('complete_mock_test_status/', StudentMockTestCompleteStatusView.as_view(), name="complete_mock_test_status"),
    path('student_app_update/', StudentApplicationIdUpdateView.as_view(), name="student_app_update"),


    path('update-student-verification-status/', CampusStudentVerifiedStatusView.as_view(), name="update-student-verification-status"),
    path('update-student-mail-status/', CampusStudentAccountMailStatusView.as_view(), name="update-student-mail-status"),


    ## download score card for refrenece
    path('student-score-card-download/', GetStudentScoreCardView.as_view(), name="student-score-card-download"),
    path('admin-student-score-card-download/<int:stid>', GetAdminStudentScoreCardView.as_view(), name="admin-student-score-card-download"),
    
    path('create_student_payment/', StudentCreatePaymentView.as_view(), name="create_student_payment"),
    path('create_student_profile_payment/', StudentProfileCreatePaymentView.as_view(), name="create_student_profile_payment"),
    path('post_exam_result/', PostExamResultView.as_view(), name="post_exam_result"),
    path('post_real_exam_result/', PostRealExamResultView.as_view(), name="post_real_exam_result"),

    
    path('student_profile_report_excel/', GetStudentProfileReportExcelView.as_view(), name="student_profile_report_excel"),
    path('student_profile_report_pdf/', GetStudentProfileReportPDFView.as_view(), name="student_profile_report_pdf"),

    path('student_interview_report_excel/', GetStudentProfileInterviewReportExcelView.as_view(), name="student_interview_report_excel"),

    path("company_dropdown_list/", DropDownInterviewCompanyView.as_view(), name="company_dropdown_list"),
    path("create_update_interview/", ManageStudentInterviewView.as_view(), name="create_update_interview"),
    path("interview_page_list/", InterviewSchedule_list.as_view(), name="interview_listing"),

    path('test_waiver_update/', AddWaiverValueProfileView.as_view(), name="test_waiver_update"),
    path('test_upload_profile_meritto/', AddProfileToMerittoView.as_view(), name="test_upload_profile_meritto"),

    
    path("schedule-assessment/",ScheduleAssessmentAPIView.as_view(),name="schedule-assessment"),

    ## admin
    path("check_blank_payment/",ReAttemptPaymentsView.as_view(),name="check_blank_payment"),
    path("meritto_update_result/",MerittoExamResultUpdateView.as_view(),name="meritto_update_result"),

]