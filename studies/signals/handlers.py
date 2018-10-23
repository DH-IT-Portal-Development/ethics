from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from studies.models import Documents, Study
from studies.utils import create_documents_for_study as create_document_object

@receiver(post_save, sender=Study)
def create_documents_for_study(sender, instance, **kwargs):
    documents = Documents.objects.filter(study=instance)

    if not documents:
        create_document_object(instance)


@receiver(pre_delete, sender=Study)
def auto_destroy_documents(sender, instance, **kwargs):
    instance.documents.delete()