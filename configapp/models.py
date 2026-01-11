from datetime import datetime, timedelta
from random import random
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from config.settings import AUTH_USER_MODEL


class CustomUser(AbstractUser):
	email = models.EmailField(unique=True)

	def __str__(self):
		return self.email


class Post(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
	photo = models.ImageField(upload_to='posts/')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.title} by {self.author}"

	@property
	def liked_user_ids(self):
		return list(self.likes.values_list('user_id', flat=True))


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Comment by {self.author} on {self.post_id}"


class Like(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('post', 'user')

	def __str__(self):
		return f"Like: {self.user} -> {self.post_id}"


class EmailVerification(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verifications')
	code = models.CharField(max_length=64)
	created_at = models.DateTimeField(auto_now_add=True)
	is_used = models.BooleanField(default=False)
	expires_at = models.DateTimeField()

	def mark_used(self):
		self.is_used = True
		self.save()

	def is_expired(self):
		return timezone.now() > self.expires_at





# //////////////////////////////////////////////////////////////////////
from django.core.validators import FileExtensionValidator 
ODINARY_USER,MANAGER,ADMIN=('ordinary_user','manager','admin')
NEW,CODE_VERIFIED,DONE,PHOTO_DONE=('new','code_verified','done','photo_done')
VIA_EMAIL,VIA_PHONE=('via_email','via_phone')


class User(abstractUser):
	USER_ROLES=(
		(ODINARY_USER,'Ordinary User'),
		(MANAGER,'Manager'),
		(ADMIN,'Admin'),
	)
	AUTH_STATUS = (

		(NEW,'New'),
		(CODE_VERIFIED,'Code Verified'),
		(DONE,'Done'),
		(PHOTO_DONE,'Photo Done'),

	)
	AUTH_TYPE = (
		(VIA_EMAIL,'Via Email'),
		(VIA_PHONE,'Via Phone'),
	)
	user_role = models.CharField(max_length=20,choices=USER_ROLES,default=ODINARY_USER)
	auth_status = models.CharField(max_length=20,choices=AUTH_STATUS,default=NEW)
	auth_type = models.CharField(max_length=20,choices=AUTH_TYPE)
	email = models.EmailField(unique=True,null=True,blank=True)
	phone_number = models.CharField(max_length=15,null=True,blank=True,unique=True)
	photo= models.ImageField(upload_to='user_photos/',null=True,blank=True,\
						  validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','.heic'])])	
	def __str__(self):
		return self.username
	def verify_code(self,verify_type):
		code = str(random.randint(1000, 9999))
		CodeVerification.objects.create(
			  user_id=self.id,
			  verify_type=verify_type,
			  code=code
			)
		return code
	
class CodeVerification(BaseModel):
	VERIFY_TYPE = (
		(VIA_EMAIL,'VIA_EMAIL'),
		(VIA_PHONE,'VIA_PHONE'),
	)
	code = models.CharField(max_length=4)
	verify_type = models.CharField(max_length=29,choices=VERIFY_TYPE)
	user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='code_verifications')
	expiration_time = models.DateTimeField(

	)
	confirmed = models.BooleanField(default=False)
	def __str__(self):
		return str(self.user.__str__()) 

	def save (self, *args, **kwargs):
		if self.verify_type == VIA_EMAIL:
			self.expiration_time = datetime.now() + timedelta(minutes=EXPIRATION_EMAIL)
		else:
			self.expiration_time = datetime.now() + timedelta(minutes=EXPIRATION_PHONE)
		super(CodeVerification, self).save(*args, **kwargs)			