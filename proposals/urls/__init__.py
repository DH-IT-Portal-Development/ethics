from .attachment_urls import attachment_urls
from .proposal_urls import proposal_urls

app_name = "proposals"
urlpatterns = []

urlpatterns += proposal_urls
urlpatterns += attachment_urls
