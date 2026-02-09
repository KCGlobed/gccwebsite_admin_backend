from django.urls import path
from .views import *

urlpatterns = [

    path("tags_dropdown", BlogTag_dropdown.as_view()),
    path("category_dropdown", BlogCategory_dropdown.as_view()),

    path("create_blog", CreateBlogView.as_view()),
    path("update_blog/<int:pk>", UpdateBlogView.as_view()),
    path("delete_blog/<int:pk>", DeleteBlogView.as_view()),
    path("blogs_list", Blogs_list.as_view()),
    
]