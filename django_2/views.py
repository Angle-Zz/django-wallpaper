import hashlib
import os
import random

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse


from .forms import MyForm
from .models import User, Image


def post_list(request):
    return render(request, 'home.html')


def hash_verification_code(password):
    # 创建SHA-256哈希对象
    sha256_hash = hashlib.sha256()

    # 将验证码编码为字节串并进行哈希处理
    sha256_hash.update(password.encode('utf-8'))

    # 获取哈希结果
    hashed_code = sha256_hash.hexdigest()

    return hashed_code


def file_extension(value):
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    print(type(value))
    if isinstance(value, InMemoryUploadedFile):
        if not value.name.lower().endswith(tuple(allowed_extensions)):
            raise ValidationError("只允许上传图片文件 (.jpg, .jpeg, .png, .gif).")
    elif isinstance(value, bytes):
        filename = value.name  # 使用源文件名作为默认文件名
        if not filename.lower().endswith(tuple(allowed_extensions)):
            raise ValidationError("只允许上传图片文件 (.jpg, .jpeg, .png, .gif).")
        return filename  # 返回文件名

#
def listdir(username):
    static_folder = os.path.join(settings.STATIC_ROOT, username).replace('\\', '/')
    file_names = os.listdir(static_folder)
    # 获取存在的图片列表
    image_files = [f for f in file_names if os.path.isfile(os.path.join(static_folder, f))]
    if len(image_files) >= 10:
        random_images = random.sample(image_files, 10)
    else:
        random_images = image_files
    return random_images

def upload_file(request):
    username = request.session.get('username')
    if username is None:
        return redirect('login')
    random_images = listdir(username)
    if request.user.is_authenticated:
        listdir(username)
        return redirect('login', {'random_images': random_images})
    else:
        # 用户一登陆，显示用户名和退出链接
        logout_link = reverse('logout')  # 退出链接
        if request.method == 'POST':
            if username is None:
                return HttpResponse('请先登录')
            files = request.FILES.getlist('file')  # 获取多个文件对象
            if files:
                try:
                    user_folder = os.path.join('django_2', 'static', username)
                    # 如果用户文件夹不存在，则创建它
                    if not os.path.exists(user_folder):
                        os.makedirs(user_folder)
                    for file in files:
                        file_extension(file)
                        file_path = os.path.join(user_folder, file.name)  # 文件保存路径
                        print(file_path)
                        # 保存文件到指定路径
                        with open(file_path, 'wb') as destination:
                            for chunk in file.chunks():
                                destination.write(chunk)

                    return redirect('upload')
                except Exception as e:
                    print(f"文件上传失败: {e}")
                    return HttpResponse('false')

        return render(request, 'upload_file.html', {'random_images': random_images, 'username': username, 'logout_link': logout_link})


def register_view(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        user_password = request.POST.get('password')
        hash_password = make_password(user_password)

        # 验证表单数据的有效性（可以根据需要自定义验证逻辑）
        form = MyForm(request.POST)
        if form.is_valid():
            # 创建数据库记录
            user = User(username=user_name, password=hash_password)
            image = Image(username=user_name, wallpaper_dir="C:/Users/48782/PycharmProjects"
                                                            "/django_2/django_2/static" + user_name)
            user.save()
            image.save()
            # 获取用户文件夹路径
            user_folder = os.path.join(settings.STATIC_ROOT, user_name)

            # 在用户文件夹中创建新的文件夹
            # new_folder = os.path.join(user_folder, user_name)
            os.makedirs(user_folder, exist_ok=True)

            return render(request, 'login.html')
        else:
            error_message = "格式错误"
            return render(request, 'register.html', {'error_message': error_message})
    else:
        form = MyForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):

    username = request.session.get('username')

    if username:
        # 用户一登陆，显示用户名和退出链接
        logout_link = reverse('logout')  # 退出链接

        # 获取随机图片
        static_folder = 'C:/Users/48782/PycharmProjects/django_2/django_2/static/wallpapers'
        file_names = os.listdir(static_folder)
        image_files = [f for f in file_names if os.path.isfile(os.path.join(static_folder, f))]
        random_images = random.sample(image_files, 10)

        return render(request, 'home.html',
                      {'random_images': random_images, 'username': username, 'logout_link': logout_link})
    else:
        # 用户未登录，显示登陆和注册链接
        login_link = reverse('login')  # 登录连接
        register_link = reverse('register')  # 注册链接
    if request.method == 'POST':
        user_name = request.POST.get('username')
        user_password = request.POST.get('password')
        # hash_password = make_password(user_password)
        try:
            user = User.objects.get(username=user_name)
            if check_password(user_password, user.password):  # 验证数据库表的哈希密码
                # 密码匹配，进行用户操作逻辑...
                request.session['username'] = user_name
                # 用户成功登录后重定向到原始请求的URL
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('home')  # 登录成功后跳转到主页
            else:
                # 密码不匹配，显示密码错误信息
                error_message = "密码错误"
                return render(request, 'login.html', {'error_message': error_message, 'username': user_name})
        except User.DoesNotExist:
            # 用户名不存在，显示用户名或密码错误信息
            error_message = "用户名不存在！"
            return render(request, 'login.html', {'error_message': error_message})

    else:
        form = MyForm()
    return render(request, 'login.html', {'form': form, 'login_link': login_link, 'register_link': register_link})


def logout_view(request):
    logout(request)
    return redirect('home')  # 重定向到主页或其他页面

def home_view(request):
    username = request.session.get('username')

    if username:
        # 用户一登陆，显示用户名和退出链接
        logout_link = reverse('logout')  # 退出链接

        # 获取随机图片
        static_folder = 'C:/Users/48782/PycharmProjects/django_2/django_2/static/wallpapers'
        file_names = os.listdir(static_folder)
        print(file_names)
        image_files = [f for f in file_names if os.path.isfile(os.path.join(static_folder, f))]
        random_images = random.sample(image_files, 10)

        return render(request, 'home.html',
                      {'random_images': random_images, 'username': username, 'logout_link': logout_link})
    else:
        # 用户未登录，显示登陆和注册链接
        login_link = reverse('login')  # 登录连接
        register_link = reverse('register')  # 注册链接

    static_folder = 'C:/Users/48782/PycharmProjects/django_2/django_2/static/wallpapers'
    file_names = os.listdir(static_folder)
    # 获取存在的图片列表
    image_files = [f for f in file_names if os.path.isfile(os.path.join(static_folder, f))]
    random_images = random.sample(image_files, 10)

    return render(request, 'home.html',
                  {'random_images': random_images,  'login_link': login_link, 'register_link': register_link})
