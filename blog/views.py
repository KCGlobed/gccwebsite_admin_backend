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


# Create your views here.


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
                "data": [{"id":cid}],
                "status":status.HTTP_400_BAD_REQUEST
            })