from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from gcc_backend.utils import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated


class HelloAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "Welcome to GCC School Learning..!!"})
    



class UserLoginView(APIView):
    # renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            email = serializer.data.get('email').lower()
            password = serializer.data.get('password')
            user = authenticate(email = email, password = password)
            if user is not None:
                
                token = get_tokens_for_user(user)
                update_last_login(None, user)

                # if user.current_refresh is not None:
                #     try:
                #         RefreshToken(user.current_refresh).blacklist()
                #     except TokenError:
                #         pass
                
                # user.current_refresh = token['refresh']
                # user.save()


                return success_response(message="Login Success", data={'token': token, 'user_role': serializer.data.get('role'), "user_id":user.id}, status_code=status.HTTP_200_OK)
            else:
                return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)
        
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    








