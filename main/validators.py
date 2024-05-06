from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy, ngettext_lazy

ALLOWED_CONTENT_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]


class MaxWordsValidator(BaseValidator):
    compare = lambda self, a, b: a > b
    clean = lambda self, x: len(x.split())
    message = ngettext_lazy(
        "Dit veld mag maximaal %(limit_value)d woord bevatten.",
        "Dit veld mag maximaal %(limit_value)d woorden bevatten.",
        "limit_value",
    )
    code = "max_words"


def validate_pdf_or_doc(value):
    f = value.file
    if isinstance(f, UploadedFile) and f.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(
            gettext_lazy("Alleen .pdf- of .doc(x)-bestanden zijn toegestaan.")
        )
