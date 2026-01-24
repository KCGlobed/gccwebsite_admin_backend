from rest_framework import serializers
from users.models import *



class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255,required=True)
    password = serializers.CharField(max_length = 255,required=True)
    role = serializers.CharField(max_length = 255,required=True)
    # device_type = serializers.CharField(max_length = 255, required=True)
    # device_id = serializers.CharField(max_length = 255, required=True)

    class Meta:
        model = User
        fields = ['email', 'password',"role"]

    def validate(self, data):
        user = User.objects.filter(email =data.get('email').lower()).first()
        if user is None:
            raise serializers.ValidationError("User Not found with this email!")
        
        if user.is_active is False:
            raise serializers.ValidationError("User is not active!")
        
        if user.email_verified == 0:
            raise serializers.ValidationError("User email is not verified!")
        
        if user:
            if not user.check_password(data.get('password')):
                raise serializers.ValidationError("Invalid Password!")
        
        return data
