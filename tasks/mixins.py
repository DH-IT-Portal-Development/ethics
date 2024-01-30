from django.core.exceptions import PermissionDenied

from .models import Session, Task


class DeletionAllowedMixin(object):
    def get_object(self, queryset=None):
        """
        Prevent deletion of a single Task/Session in a Session/Study.
        """
        obj = super(DeletionAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Session):
            if obj.study.sessions_number() == 1:
                raise PermissionDenied
        elif isinstance(obj, Task):
            if obj.session.tasks_number() == 1:
                raise PermissionDenied

        return obj
