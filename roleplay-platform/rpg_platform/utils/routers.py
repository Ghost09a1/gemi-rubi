from rest_framework.routers import DefaultRouter
from rest_framework.versioning import URLPathVersioning


class VersionedRouter(DefaultRouter):
    """
    Custom router that supports API versioning
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.versioning_class = URLPathVersioning

    def get_urls(self):
        """
        Generate the URL patterns for the router with versioning.
        """
        return super().get_urls()
