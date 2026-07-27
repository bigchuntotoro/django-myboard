from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # 관리자 페이지
    path('admin/', admin.site.urls),
    
    # 게시판 앱 URL
    path('board/', include('board.urls')),
    
    # django-allauth URL (카카오 로그인, 로그아웃 등)
    path('accounts/', include('allauth.urls')),
    
    # 🟢 [추가] 루트 주소 접속 시 /board/ 로 자동 이동
    path('', RedirectView.as_view(url='/board/', permanent=False)),
]