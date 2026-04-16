from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework import filters
from gcc_backend.pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from google.cloud import storage
import os
import pandas as pd
import tempfile
import re
from datetime import datetime, timedelta
client = storage.Client(project=settings.GS_PROJECT_ID)
from rest_framework import status
from django.utils.dateparse import parse_date

# Create your views here.



class CreateTagView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = ListTagSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            return Response({
            'success': True,
            'message': 'Tag created successfully',
            "status": str(status.HTTP_200_OK),
            "data": serializer.data
            })
        return Response({
            'success': False,
            'message': 'Failed',
            "status": str(status.HTTP_400_BAD_REQUEST),
            "data": serializer.errors
        })
    


class UpdateTagView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            obj = Tag.objects.get(id=pk)
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found"}, status=404)

        serializer = ListTagSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Tag updated successfully",
            "data": serializer.data
        })





class BlogTag_dropdown(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        datas = Tag.objects.filter(status=True)
        serializers = ListTagSerializer(datas, many=True)
        return Response({
            'success': True,
            'message': 'Success',
            "status": str(status.HTTP_200_OK),
            "data": serializers.data
        })
    

class DeleteTagView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk, format=None):
        try:
            course = Tag.objects.get(id = pk)
            course.delete()
            return Response({
                "success": True,
                "message": "Tag Deleted Successfully",
                "data": [{"id":pk}],
                "status":status.HTTP_200_OK
            })
        except Tag.DoesNotExist:
            return Response({
                "success": False,
                "message": "Tag not found",
                "data": [{"id":pk}],
                "status":status.HTTP_400_BAD_REQUEST
            })




class CreateCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = ListCategorySerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            return Response({
            'success': True,
            'message': 'Category created successfully',
            "status": str(status.HTTP_200_OK),
            "data": serializer.data
            })
        return Response({
            'success': False,
            'message': 'Failed',
            "status": str(status.HTTP_400_BAD_REQUEST),
            "data": serializer.errors
        })
    


class UpdateCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            obj = Category.objects.get(id=pk)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)

        serializer = ListCategorySerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Category updated successfully",
            "data": serializer.data
        })

    

class DeleteCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk, format=None):
        try:
            course = Category.objects.get(id = pk)
            course.delete()
            return Response({
                "success": True,
                "message": "Category Deleted Successfully",
                "data": [{"id":pk}],
                "status":status.HTTP_200_OK
            })
        except Category.DoesNotExist:
            return Response({
                "success": False,
                "message": "Category not found",
                "data": [{"id":pk}],
                "status":status.HTTP_400_BAD_REQUEST
            })



class BlogCategory_dropdown(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        datas = Category.objects.filter(status=True)
        serializers = ListCategorySerializer(datas, many=True)
        return Response({
            'success': True,
            'message': 'Success',
            "status": str(status.HTTP_200_OK),
            "data": serializers.data
        })
    

class CreateBlogView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateBlogSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            return Response({
            'success': True,
            'message': 'Blog created successfully',
            "status": str(status.HTTP_200_OK),
            "data": serializer.data
            })
        return Response({
            'success': False,
            'message': 'Failed',
            "status": str(status.HTTP_400_BAD_REQUEST),
            "data": serializer.errors
        })
    


class UpdateBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            obj = Blog.objects.get(id=pk)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=404)

        serializer = UpdateBlogSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Blog updated successfully",
            "data": serializer.data
        })

    

class Blogs_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = Blog.objects.all().order_by('-id')

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)

        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListingBlogSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    

class DeleteBlogView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, pk, format=None):
        try:
            course = Blog.objects.get(id = pk)
            course.delete()
            return Response({
                "success": True,
                "message": "Blog Deleted Successfully",
                "data": [{"id":pk}],
                "status":status.HTTP_200_OK
            })
        except Blog.DoesNotExist:
            return Response({
                "success": False,
                "message": "Blog not found",
                "data": [{"id":pk}],
                "status":status.HTTP_400_BAD_REQUEST
            })
        



##################################### For Website ####################################


class WebsiteBlogs_list(APIView):
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['id']
    def get(self, request):
        datas = Blog.objects.filter(status=True).order_by('-id')

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)

        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListingBlogSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    




class WebsiteBlogs_detail(APIView):
    def get(self, request, pk):

        datas = Blog.objects.filter(id=pk, status=True)
        serializers = ListingBlogSerializer(datas, many=True).data
        
        return Response({
                "success": True,
                "message": "Success",
                "data": serializers,
                "status":status.HTTP_200_OK
            })
    



#################################### Seminar Event Manage ################################


class CreateManageSeminarView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateUpdateSeminarSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            return Response({
            'success': True,
            'message': 'Seminar created successfully',
            "status": str(status.HTTP_200_OK),
            "data": serializer.data
            })
        return Response({
            'success': False,
            'message': 'Failed',
            "status": str(status.HTTP_400_BAD_REQUEST),
            "data": serializer.errors
        })



class Seminar_list(APIView):
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = ManageSeminar.objects.all().order_by('-id')

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)

        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ManageSeminarSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    



class UpdateSeminarView(APIView):
    # permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            obj = ManageSeminar.objects.get(id=pk)
        except ManageSeminar.DoesNotExist:
            return Response({"error": "Seminar not found"}, status=404)

        serializer = CreateUpdateSeminarSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Seminar updated successfully",
            "data": serializer.data
        })

class DeleteSeminarView(APIView):
    # permission_classes = [IsAuthenticated]
    def delete(self, request, pk, format=None):
        try:
            course = ManageSeminar.objects.get(id = pk)
            course.delete()
            return Response({
                "success": True,
                "message": "Seminar Deleted Successfully",
                "data": [{"id":pk}],
                "status":status.HTTP_200_OK
            })
        except ManageSeminar.DoesNotExist:
            return Response({
                "success": False,
                "message": "Seminar not found",
                "data": [{"id":pk}],
                "status":status.HTTP_400_BAD_REQUEST
            })
        

class ChangeSeminarStatusView(APIView):
    # permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            obj = ManageSeminar.objects.get(id=pk)
        except ManageSeminar.DoesNotExist:
            return Response({"error": "Seminar not found"}, status=404)

        serializer = ChangeSeminarStatusSerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Seminar status updated successfully",
            "data": serializer.data
        })


##### WEbsites ####

class WebsiteSeminar_list(APIView):
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = ManageSeminar.objects.all().order_by('-id')

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)

        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = WebsiteManageSeminarSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    


