from django.urls import path
from .api_views import UserProfileXPView, UserBadgeListView

urlpatterns = [
    path('profile/', UserProfileXPView.as_view(), name='xp-profile'),
    path('badges/', UserBadgeListView.as_view(), name='user-badges'),
]
