from rest_framework import serializers
from .models import *



class ListTagSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Tag
        fields = "__all__"


class ListCategorySerializer(serializers.ModelSerializer) :
    class Meta:
        model = Category
        fields = "__all__"


class CreateBlogSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Blog
        fields = "__all__"




class UpdateBlogSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=False
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )

    class Meta:
        model = Blog
        fields = "__all__"

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        categories = validated_data.pop("categories", None)

        # Update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update M2M
        if tags is not None:
            instance.tags.set(tags)

        if categories is not None:
            instance.categories.set(categories)

        return instance






class ListingBlogSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Blog
        fields = "__all__"
        depth = 1




######################################## Seminar Event Manage ##################################################


class CreateUpdateSeminarSerializer(serializers.ModelSerializer) :
    class Meta:
        model = ManageSeminar
        fields = ["title","content","thumbnailImage","tags","event_link"]

class ManageSeminarSerializer(serializers.ModelSerializer) :
    class Meta:
        model = ManageSeminar
        fields = "__all__"

class ChangeSeminarStatusSerializer(serializers.ModelSerializer) :
    class Meta:
        model = ManageSeminar
        fields = ["status"]


class WebsiteManageSeminarSerializer(serializers.ModelSerializer) :
    class Meta:
        model = ManageSeminar
        # fields = "__all__"
        exclude = ["status"]