import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Project root: {ROOT}")

# 1. Update backend/apps/gamification/models.py
models_path = os.path.join(ROOT, "backend", "apps", "gamification", "models.py")
with open(models_path, "r", encoding="utf-8") as f:
    models_content = f.read()

models_to_add = '''

class SpinWheelSegment(models.Model):
    """
    Phase 1.2: Configurable Daily Spin Wheel segment with custom label, reward coins, color, and probability weight.
    """
    label = models.CharField(max_length=100, help_text="Display label on wheel segment, e.g. '50 Coins'")
    reward_coins = models.PositiveIntegerField(default=10, help_text="Number of coins awarded when landed")
    weight = models.PositiveIntegerField(default=10, help_text="Probability weight percentage (1-100)")
    color = models.CharField(max_length=20, default="#6366F1", help_text="Hex color code for wheel segment UI")
    is_active = models.BooleanField(default=True, help_text="Whether this segment is active on the wheel")
    order = models.PositiveIntegerField(default=0, help_text="Display order on wheel (1-12)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Spin Wheel Segment"
        verbose_name_plural = "Spin Wheel Segments"

    def __str__(self):
        return f"[{self.order}] {self.label} (+{self.reward_coins}c, {self.weight}%)"


class DailySpinRecord(models.Model):
    """
    Phase 1.2: Tracks daily spins per user (1 spin per day strictly enforced).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_spin_records')
    spin_date = models.DateField(default=timezone.now, db_index=True)
    segment_won = models.ForeignKey(SpinWheelSegment, on_delete=models.SET_NULL, null=True, blank=True, related_name='spin_wins')
    coins_won = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'spin_date')
        ordering = ['-created_at']
        verbose_name = "Daily Spin Record"
        verbose_name_plural = "Daily Spin Records"

    def __str__(self):
        return f"{self.user.username} | {self.spin_date} -> {self.segment_won.label if self.segment_won else 'Coins'} (+{self.coins_won}c)"
'''

if "class SpinWheelSegment" not in models_content:
    models_content = models_content.rstrip() + "\n" + models_to_add
    with open(models_path, "w", encoding="utf-8") as f:
        f.write(models_content)
    print("models.py updated with SpinWheelSegment and DailySpinRecord.")
else:
    print("models.py already contains SpinWheelSegment.")

# 2. Update backend/apps/admin_api/views.py
views_path = os.path.join(ROOT, "backend", "apps", "admin_api", "views.py")
with open(views_path, "r", encoding="utf-8") as f:
    views_content = f.read()

# Ensure imports
if "SpinWheelSegment" not in views_content:
    views_content = views_content.replace(
        "from apps.gamification.models import StreakSettings",
        "from apps.gamification.models import StreakSettings, SpinWheelSegment"
    )
if "AdminSpinWheelSegmentSerializer" not in views_content:
    views_content = views_content.replace(
        "    AdminStreakSettingsSerializer,\n)",
        "    AdminStreakSettingsSerializer,\n    AdminSpinWheelSegmentSerializer,\n)"
    )

viewset_to_add = '''

class AdminSpinWheelSegmentViewSet(viewsets.ModelViewSet):
    """
    Phase 1.2: Admin ViewSet to manage spin wheel segments and probability weights.
    """
    permission_classes = [IsAdminOrStaff]
    queryset = SpinWheelSegment.objects.all().order_by('order')
    serializer_class = AdminSpinWheelSegmentSerializer

    @action(detail=False, methods=['post'], url_path='reset_defaults')
    def reset_defaults(self, request):
        from apps.gamification.services.spin_service import DEFAULT_12_SEGMENTS
        from django.db import transaction
        with transaction.atomic():
            SpinWheelSegment.objects.all().delete()
            created = []
            for item in DEFAULT_12_SEGMENTS:
                created.append(SpinWheelSegment(**item))
            SpinWheelSegment.objects.bulk_create(created)

        serializer = self.get_serializer(SpinWheelSegment.objects.all().order_by('order'), many=True)
        return Response({
            'success': True,
            'message': 'Successfully reset to default 12-segment wheel.',
            'count': len(serializer.data),
            'segments': serializer.data,
        }, status=status.HTTP_200_OK)
'''

if "class AdminSpinWheelSegmentViewSet" not in views_content:
    views_content = views_content.rstrip() + "\n" + viewset_to_add
    with open(views_path, "w", encoding="utf-8") as f:
        f.write(views_content)
    print("views.py updated with AdminSpinWheelSegmentViewSet.")
else:
    print("views.py already contains AdminSpinWheelSegmentViewSet.")

# 3. Rewrite backend/apps/admin_api/urls.py
urls_path = os.path.join(ROOT, "backend", "apps", "admin_api", "urls.py")
urls_full = '''from django.urls import path, include
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
)

router = DefaultRouter()
router.register(r'tasks', AdminVideoTaskViewSet, basename='admin-tasks')
router.register(r'watch-sessions', AdminWatchSessionViewSet, basename='admin-watch-sessions')
router.register(r'users', AdminUserViewSet, basename='admin-users')
router.register(r'wallet-transactions', AdminWalletTransactionViewSet, basename='admin-wallet-transactions')
router.register(r'spin-wheel-segments', AdminSpinWheelSegmentViewSet, basename='admin-spin-wheel-segments')

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('ai-settings/', AdminAISettingsView.as_view(), name='admin-ai-settings'),
    path('ai-settings/fetch-models/', AdminAIFetchModelsView.as_view(), name='admin-ai-fetch-models'),
    path('ai-settings/test-sandbox/', AdminAITestSandboxView.as_view(), name='admin-ai-test-sandbox'),
    path('gamification-settings/', AdminStreakSettingsView.as_view(), name='admin-gamification-settings'),
    path('tokens/', AdminTokenBlacklistView.as_view(), name='admin-tokens'),
    path('', include(router.urls)),
]
'''
with open(urls_path, "w", encoding="utf-8") as f:
    f.write(urls_full)
print("urls.py rewritten with AdminSpinWheelSegmentViewSet and spin-wheel-segments route.")

# 4. Insert into admin-frontend/src/api/adminApi.js
admin_api_path = os.path.join(ROOT, "admin-frontend", "src", "api", "adminApi.js")
with open(admin_api_path, "r", encoding="utf-8") as f:
    api_content = f.read()

spin_api_code = '''
  // Daily Spin Wheel Configuration
  getSpinWheelSegments: async () => {
    const res = await apiClient.get('/admin/spin-wheel-segments/');
    return res.data;
  },
  createSpinWheelSegment: async (data) => {
    const res = await apiClient.post('/admin/spin-wheel-segments/', data);
    return res.data;
  },
  updateSpinWheelSegment: async (id, data) => {
    const res = await apiClient.put(`/admin/spin-wheel-segments/${id}/`, data);
    return res.data;
  },
  patchSpinWheelSegment: async (id, data) => {
    const res = await apiClient.patch(`/admin/spin-wheel-segments/${id}/`, data);
    return res.data;
  },
  deleteSpinWheelSegment: async (id) => {
    const res = await apiClient.delete(`/admin/spin-wheel-segments/${id}/`);
    return res.data;
  },
  resetSpinWheelDefaults: async () => {
    const res = await apiClient.post('/admin/spin-wheel-segments/reset_defaults/');
    return res.data;
  },
'''

if "getSpinWheelSegments" not in api_content:
    last_brace_index = api_content.rfind("};")
    if last_brace_index != -1:
        api_content = api_content[:last_brace_index] + spin_api_code + api_content[last_brace_index:]
        with open(admin_api_path, "w", encoding="utf-8") as f:
            f.write(api_content)
        print("adminApi.js updated with spin wheel methods.")
    else:
        print("Could not find closing '};' in adminApi.js")
else:
    print("adminApi.js already contains getSpinWheelSegments.")

# 5. Update admin-frontend/src/App.jsx
app_jsx_path = os.path.join(ROOT, "admin-frontend", "src", "App.jsx")
with open(app_jsx_path, "r", encoding="utf-8") as f:
    app_content = f.read()

if "SpinWheelSettingsPage" not in app_content:
    app_content = app_content.replace(
        "import { GamificationSettingsPage } from './pages/GamificationSettingsPage';",
        "import { GamificationSettingsPage } from './pages/GamificationSettingsPage';\nimport { SpinWheelSettingsPage } from './pages/SpinWheelSettingsPage';"
    )
if '<Route path="spin-wheel"' not in app_content:
    app_content = app_content.replace(
        '<Route path="gamification" element={<GamificationSettingsPage />} />',
        '<Route path="gamification" element={<GamificationSettingsPage />} />\n              <Route path="spin-wheel" element={<SpinWheelSettingsPage />} />'
    )
with open(app_jsx_path, "w", encoding="utf-8") as f:
    f.write(app_content)
print("App.jsx verified / updated with SpinWheelSettingsPage.")

# 6. Update admin-frontend/src/components/layout/Sidebar.jsx
sidebar_path = os.path.join(ROOT, "admin-frontend", "src", "components", "layout", "Sidebar.jsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    sidebar_content = f.read()

if "PieChart" not in sidebar_content:
    sidebar_content = sidebar_content.replace(
        "  Trophy,\n",
        "  Trophy,\n  PieChart,\n"
    )
if "'/spin-wheel'" not in sidebar_content:
    sidebar_content = sidebar_content.replace(
        "{ to: '/gamification', label: 'Gamification Settings', icon: Trophy },",
        "{ to: '/gamification', label: 'Gamification Settings', icon: Trophy },\n    { to: '/spin-wheel', label: 'Spin Wheel', icon: PieChart },"
    )
with open(sidebar_path, "w", encoding="utf-8") as f:
    f.write(sidebar_content)
print("Sidebar.jsx verified / updated with PieChart and spin-wheel nav item.")

# 7. Update admin-frontend/src/components/layout/AdminLayout.jsx
admin_layout_path = os.path.join(ROOT, "admin-frontend", "src", "components", "layout", "AdminLayout.jsx")
with open(admin_layout_path, "r", encoding="utf-8") as f:
    layout_content = f.read()

if "'/spin-wheel'" not in layout_content:
    layout_content = layout_content.replace(
        "case '/gamification': return 'Gamification Settings';",
        "case '/gamification': return 'Gamification Settings';\n      case '/spin-wheel': return 'Spin Wheel Configuration';"
    )
    with open(admin_layout_path, "w", encoding="utf-8") as f:
        f.write(layout_content)
    print("AdminLayout.jsx updated with /spin-wheel title case.")
else:
    print("AdminLayout.jsx already contains /spin-wheel.")

print("All shell updates completed successfully.")
