from django.db.models import Q
from rest_framework import serializers, status
from .models import CodeVerify, CustomUser, VIA_EMAIL, VIA_PHONE, CODE_VERIFY, DONE, PHOTO_DONE
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from shared.utility import check_email_or_phone, check_email_or_phone_or_username
class SignupSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_status = serializers.CharField(read_only=True)
    auth_type = serializers.CharField(read_only=True)

    def __init__(self, instance=None, **kwargs):
        super().__init__(instance, **kwargs)
        self.fields['email_or_phone']= serializers.CharField(write_only=True, required=True)


    class Meta:
        model = CustomUser
        fields = ('id', 'auth_status', 'auth_type')


    def create(self, validated_data):
        user=super().create(validated_data)
        if user.auth_type==VIA_EMAIL:
            code=user.generate_code(VIA_EMAIL)
            print(code,'||||||||||||||||||')
        elif user.auth_type==VIA_PHONE:
            code=user.generate_code(VIA_PHONE)
            print(code,'||||||||||||||||||')
        else:
            raise ValidationError('Email yoki telefon raqami xato')
        user.save()
        return user



    def validate(self, attrs):
        super().validate(attrs)
        data=self.auth_validate(attrs)
        return data

    @staticmethod
    def auth_validate(data):
        user_input=data.get('email_or_phone')
        user_input_type = check_email_or_phone(user_input)

        if user_input_type == 'phone':
            data={
                'auth_type':VIA_PHONE,
                'phone_number':user_input
            }
        elif user_input_type == 'email':
            data={
                'auth_type':VIA_EMAIL,
                'email':user_input
            }
        else:
            response = {
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Phone or email address not valid"
            }
            raise ValidationError(response)
        return data

    def validate_email_or_phone(self, email_or_phone):
        user=CustomUser.objects.filter(Q(email=email_or_phone) | Q(phone=email_or_phone)).first()
        if user:
            raise ValidationError(detail='bu email yoki telefon raqami bilan oldin royxatdan otilgan')
        return email_or_phone




    def to_representation(self, instance):
        data=super().to_representation(instance)
        data['message']='kodingiz yuborildi'
        data['refresh']=instance.token()['refresh']
        data['access']=instance.token()['access']
        return data




class UserChangeInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)

        if password is None or confirm_password is None or password != confirm_password:
            response = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Parollar mos emas yoki xato kiritildi'
            }
            raise ValidationError(response)
        if len([i for i in password if i == ' ']) > 4:
            response = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Parollar xato kiritildi'
            }
            raise ValidationError(response)

        return data

    def validate_username(self, username):
        if len(username) < 6:
            raise ValidationError({'message': 'Username kamida 7 ta bolishi kerak'})
        elif not username.isalnum() or username.isdigit():
            raise ValidationError({'message': 'Username da ortiqcha belgilar bolmasligi kerak'})
        elif username[0].isdigit():
            raise ValidationError({'message': 'Username raqam bilan boshlanmasin'})
        return username

    def validate_first_name(self,first_name):
        first_name = first_name.strip()
        if not first_name:
            raise serializers.ValidationError("Ism bo'sh bo'lishi mumkin emas.")
        if len(first_name) < 3:
            raise serializers.ValidationError("Ism kamida 3 ta belgidan iborat bo'lishi kerak.")
        if len(first_name) > 50:
            raise serializers.ValidationError("Ism 50 ta belgidan oshmasligi kerak.")
        if not first_name.isalpha() or first_name[0]=="'" or not first_name.replace("'",'').isalpha():
            raise serializers.ValidationError("Ism faqat harflardan iborat bo'lishi kerak.")
        return first_name.capitalize()

    def validate_last_name(self, last_name):
        last_name = last_name.strip()
        if not last_name:
            raise serializers.ValidationError("Familiya bo'sh bo'lishi mumkin emas.")
        if len(last_name) < 2:
            raise serializers.ValidationError("Familiya kamida 2 ta belgidan iborat bo'lishi kerak.")
        if len(last_name) > 50:
            raise serializers.ValidationError("Familiya 50 ta belgidan oshmasligi kerak.")
        if not last_name.isalpha():
            raise serializers.ValidationError("Familiya faqat harflardan iborat bo'lishi kerak.")
        return last_name.capitalize()

    def update(self, instance, validated_data):
        if instance.auth_status != CODE_VERIFY:
            raise ValidationError({"message": "siz hali tasdiqlanmagansiz ",'status':status.HTTP_400_BAD_REQUEST})
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.username = validated_data.get('username')
        instance.set_password(validated_data.get('password'))
        instance.auth_status = DONE
        instance.save()
        return instance


class UserPhotoStatusSerializer(serializers.Serializer):
    photo=serializers.ImageField()

    def update(self,instance,validated_data):
        photo=validated_data.get['photo',None]
        if photo:
            instance.photo=photo
        if instance.auth_status== DONE:
            instance.auth_status = PHOTO_DONE
        instance.save()
        return instance


class LoginSerializer(TokenObtainPairView):
    password=serializers.CharField(required=True,write_only=True)

    def __init__(self,*args,**kwargs):
        super(LoginSerializer).__init__(*args,**kwargs)
        self.fields['user_input']=serializers.CharField(required=True,write_only=True)
        self.fields['username']=serializers.CharField(read_only=True)

    def validate(self, attrs):
        data = self.check_user_type(attrs)
        return data


    @staticmethod
    def check_user_type(self, data):
        password = data.get('password')
        user_input_data=data.get('user_input')
        user_type=check_email_or_phone_or_username(user_input_data)
        if user_type=='username':
            user = CustomUser.objects.filter(username=user_input_data)
            self.get_object(user)
            username=user_input_data
        elif user_type=='email':
            user=CustomUser.objects.filter(email=user_input_data).first()
            self.get_object(user)
            username = user.username

        elif user_type == 'phone':
            user = CustomUser.objects.filter(phone=user_input_data)
            self.get_object(user)
            username = user.username

        else:
            raise ValidationError(detail="Ma'lumot topilmadi")
        authentication_kwargs = {
            "password": password,
            self.username_field: username
        }

        if user.auth_login not in [DONE, PHOTO_DONE]:
            raise ValidationError(detail="Hali Tasdiqlanmadi")
        user = authenticate(**authentication_kwargs)
        if not user:
            raise ValidationError(detail="Login yoki parol xato")

    def get_object(user):
        # user=CustomUser.objects.filter(Q(username=user_input)|Q(email=user_input)|Q(phone_number=user_input))
        if not user:
            raise ValidationError({"message": "Xato ma'lumot kiritdingiz", "status": status.HTTP_400_BAD_REQUEST})
        return True


