from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


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

