from django.urls import path
from .views import *

urlpatterns = [

    path("tags_dropdown", BlogTag_dropdown.as_view()),
    path("create_tag", CreateTagView.as_view()),
    path("update_tag/<int:pk>", UpdateTagView.as_view()),
    path("delete_tag/<int:pk>", DeleteTagView.as_view()),


    path("category_dropdown", BlogCategory_dropdown.as_view()),
    path("create_category", CreateCategoryView.as_view()),
    path("update_category/<int:pk>", UpdateCategoryView.as_view()),
    path("delete_category/<int:pk>", DeleteCategoryView.as_view()),


    path("create_blog", CreateBlogView.as_view()),
    path("update_blog/<int:pk>", UpdateBlogView.as_view()),
    path("delete_blog/<int:pk>", DeleteBlogView.as_view()),
    path("blogs_list", Blogs_list.as_view()),
    
    
    path("create_seminar", CreateManageSeminarView.as_view()),
    path("seminar_page_list", Seminar_list.as_view()),
    path("update_seminar/<int:pk>", UpdateSeminarView.as_view()),
    path("delete_seminar/<int:pk>", DeleteSeminarView.as_view()),
    path("change_seminar_status/<int:pk>", ChangeSeminarStatusView.as_view()),
    path("website_seminar_page_list", WebsiteSeminar_list.as_view()),


    ## Websites 
    path("websiteblogs_list", WebsiteBlogs_list.as_view()),
    path("websiteblogs_detail/<int:pk>", WebsiteBlogs_detail.as_view()),


]