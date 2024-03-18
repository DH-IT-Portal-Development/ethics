from django.views import generic

from .models import Faq


class FaqsView(generic.ListView):
    model = Faq
    context_object_name = "faqs"
