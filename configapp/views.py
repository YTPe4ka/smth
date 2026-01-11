from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import uuid

from .forms import RegisterForm, LoginForm, PostForm, CommentForm
from .models import Post, Comment, Like, EmailVerification


def register_view(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = False
			user.save()

			code = uuid.uuid4().hex[:6]
			expires = timezone.now() + timedelta(days=1)
			ver = EmailVerification.objects.create(user=user, code=code, expires_at=expires)

			subject = 'Email verification code'
			message = f'Your verification code: {code}'
			from_email = settings.DEFAULT_FROM_EMAIL
			recipient = [user.email]
			send_mail(subject, message, from_email, recipient, fail_silently=True)

			messages.success(request, 'Account created. Check your email for a verification code.')
			return redirect('configapp:verify', user_id=user.id)
	else:
		form = RegisterForm()
	return render(request, 'configapp/register.html', {'form': form})


def verify_view(request, user_id):
	user = get_object_or_404(settings.AUTH_USER_MODEL, pk=user_id) if False else None
	from django.contrib.auth import get_user_model
	User = get_user_model()
	user = get_object_or_404(User, pk=user_id)

	if request.method == 'POST':
		code = request.POST.get('code')
		try:
			ver = EmailVerification.objects.get(user=user, code=code, is_used=False)
		except EmailVerification.DoesNotExist:
			ver = None

		if ver and not ver.is_expired():
			user.is_active = True
			user.save()
			ver.mark_used()
			messages.success(request, 'Email verified. You can now log in.')
			return redirect('configapp:login')
		else:
			messages.error(request, 'Invalid or expired code')
			return render(request, 'configapp/verify.html', {'user': user})

	return render(request, 'configapp/verify.html', {'user': user})


def login_view(request):
	if request.method == 'POST':
		identifier = request.POST.get('username')
		password = request.POST.get('password')
		from django.contrib.auth import get_user_model
		User = get_user_model()
		user_obj = None
		if identifier and '@' in identifier:
			user_obj = User.objects.filter(email__iexact=identifier).first()
		else:
			user_obj = User.objects.filter(username__iexact=identifier).first()

		user = None
		if user_obj:
			user = authenticate(request, username=user_obj.username, password=password)
		else:
			user = authenticate(request, username=identifier, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('configapp:post_list')
			else:
				messages.error(request, 'Account inactive. Please verify your email.')
		else:
			messages.error(request, 'Invalid credentials')

	return render(request, 'configapp/login.html', {'form': LoginForm(request)})


def logout_view(request):
	logout(request)
	return redirect('configapp:login')


def post_list(request):
	posts = Post.objects.all().order_by('-created_at')
	return render(request, 'configapp/post_list.html', {'posts': posts})


def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	comment_form = CommentForm()
	return render(request, 'configapp/post_detail.html', {'post': post, 'comment_form': comment_form})


def is_admin(user):
	return user.is_active and user.is_staff


@user_passes_test(is_admin)
def create_post(request):
	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.save()
			return redirect('configapp:post_detail', pk=post.pk)
	else:
		form = PostForm()
	return render(request, 'configapp/post_form.html', {'form': form})


@user_passes_test(is_admin)
def edit_post(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES, instance=post)
		if form.is_valid():
			form.save()
			return redirect('configapp:post_detail', pk=post.pk)
	else:
		form = PostForm(instance=post)
	return render(request, 'configapp/post_form.html', {'form': form, 'post': post})


@user_passes_test(is_admin)
def delete_post(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == 'POST':
		post.delete()
		return redirect('configapp:post_list')
	return render(request, 'configapp/post_confirm_delete.html', {'post': post})

@login_required
def toggle_like(request, pk):
	post = get_object_or_404(Post, pk=pk)
	like, created = Like.objects.get_or_create(post=post, user=request.user)
	if not created:
		like.delete()
	return redirect('configapp:post_detail', pk=pk)


@login_required
def add_comment(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.author = request.user
			comment.save()
	return redirect('configapp:post_detail', pk=pk)



#///////////////////////////////////////////////////////
# from rest_framework.pagination import PageNumberPagination

# class CustomPagination(PageNumberPagination):
#     page_size = 2               # Har bir sahifada 5 ta obyekt
#     page_size_query_param = 'page_size'  # So‘rovda o‘zgartirish uchun
#     max_page_size = 100
#///////////////////////////////////////////////////////





