from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardStatsView,
    AdminVideoTaskViewSet,
    AdminWatchSessionViewSet,
    AdminUserViewSet,
    AdminWalletTransactionViewSet,
    AdminAISettingsView,
    AdminAIFetchModelsView,
    AdminAITestSandboxView,
    AdminTokenBlacklistView,
    AdminStreakSettingsView,
    AdminSpinWheelSegmentViewSet,
    AdminXPSettingsView,
    AdminBadgeViewSet,
)

router = DefaultRouter()
router.register(r'tasks', AdminVideoTaskViewSet, basename='admin-tasks')
router.register(r'watch-sessions', AdminWatchSessionViewSet, basename='admin-watch-sessions')
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'wallet-transactions', AdminWalletTransactionViewSet, basename='admin-wallet-transactions')
router.register(r'spin-wheel-segments', AdminSpinWheelSegmentViewSet, basename='admin-spin-wheel-segments')
router.register(r'badges', AdminBadgeViewSet, basename='admin-badges')

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('ai-settings/', AdminAISettingsView.as_view(), name='admin-ai-settings'),
    path('ai-settings/fetch-models/', AdminAIFetchModelsView.as_view(), name='admin-ai-fetch-models'),
    path('ai-settings/test-sandbox/', AdminAITestSandboxView.as_view(), name='admin-ai-test-sandbox'),
    path('gamification-settings/', AdminStreakSettingsView.as_view(), name='admin-gamification-settings'),
    path('xp-settings/', AdminXPSettingsView.as_view(), name='admin-xp-settings'),
    path('tokens/', AdminTokenBlacklistView.as_view(), name='admin-tokens'),
    path('', include(router.urls)),
]
