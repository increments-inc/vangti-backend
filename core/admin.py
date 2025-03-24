from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, UserInformation, UserFirebaseToken
from transactions.models import UserTransaction, UserTransactionResponse
from locations.models import UserLocation
from analytics.models import Analytics, UserRating, AppFeedback
from subscription.models import Subscription
from user_setting.models import UserSetting, VangtiTerms

# User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number', 'email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('phone_number', 'email')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

# User Information Admin
class UserInformationAdmin(admin.ModelAdmin):
    list_display = ('user', 'person_name', 'acc_type')
    search_fields = ('person_name', 'user__phone_number')
    list_filter = ('acc_type',)

# User Firebase Token Admin
class UserFirebaseTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'firebase_token', 'created_at')
    search_fields = ('user__phone_number', 'firebase_token')
    list_filter = ('created_at',)

# Transaction Admin
class UserTransactionAdmin(admin.ModelAdmin):
    list_display = ('seeker', 'provider', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('seeker__phone_number', 'provider__phone_number')
    readonly_fields = ('created_at', 'updated_at')

# Transaction Response Admin
class UserTransactionResponseAdmin(admin.ModelAdmin):
    list_display = ('seeker', 'provider', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('seeker__phone_number', 'provider__phone_number')
    readonly_fields = ('created_at', 'updated_at')

# Location Admin
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'latitude', 'longitude', 'updated_at')
    search_fields = ('user__phone_number',)
    list_filter = ('updated_at',)

# Analytics Admin
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'no_of_transaction', 'profit', 'total_amount_of_transaction')
    search_fields = ('user__phone_number',)
    readonly_fields = ('created_at', 'updated_at')

# User Rating Admin
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__phone_number',)

# App Feedback Admin
class AppFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__phone_number', 'message')

# Subscription Admin
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    list_filter = ('plan', 'status', 'start_date', 'end_date')
    search_fields = ('user__phone_number',)
    readonly_fields = ('created_at', 'updated_at')

# User Setting Admin
class UserSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'accepted_terms')
    list_filter = ('language', 'accepted_terms')
    search_fields = ('user__phone_number',)

# Vangti Terms Admin
class VangtiTermsAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserInformation, UserInformationAdmin)
admin.site.register(UserFirebaseToken, UserFirebaseTokenAdmin)
admin.site.register(UserTransaction, UserTransactionAdmin)
admin.site.register(UserTransactionResponse, UserTransactionResponseAdmin)
admin.site.register(UserLocation, UserLocationAdmin)
admin.site.register(Analytics, AnalyticsAdmin)
admin.site.register(UserRating, UserRatingAdmin)
admin.site.register(AppFeedback, AppFeedbackAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSetting, UserSettingAdmin)
admin.site.register(VangtiTerms, VangtiTermsAdmin) 