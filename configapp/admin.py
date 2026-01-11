from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post, Comment, Like, EmailVerification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	model = CustomUser
	list_display = ('username', 'email', 'is_staff', 'is_active')
	list_filter = ('is_staff', 'is_active')
	fieldsets = (
		(None, {'fields': ('username', 'email', 'password')}),
		('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')
		}),
	)
	search_fields = ('email', 'username')
	ordering = ('email',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'created_at')
	search_fields = ('title', 'description')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('post', 'author', 'created_at')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
	list_display = ('post', 'user', 'created_at')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
	list_display = ('user', 'code', 'is_used', 'expires_at')
