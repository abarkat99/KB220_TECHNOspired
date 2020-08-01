from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


class CustomAdminSite(admin.AdminSite):

    def get_urls(self):
        urls = super(CustomAdminSite, self).get_urls()
        custom_urls = [
            path('charts/', self.admin_view(), name="charts"),
        ]
        return urls + custom_urls

urlpatterns = [
    path('', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)