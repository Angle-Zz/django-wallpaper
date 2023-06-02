from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=200)
    join_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user'

class Image(models.Model):
    username = models.CharField(max_length=100, unique=True)
    wallpaper_dir = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wallpaper_user'

    # 在 UserCaptcha 中，使用 ForeignKey 字段来与用户模型建立一对多关系，通过 related_name 参数指定了反向关系的名称，即通过用户模型可以访问到与之关联的图片模型。


"""
class UserCaptcha(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_captcha')
    username = models.CharField(max_length=100, null=False)
"""
