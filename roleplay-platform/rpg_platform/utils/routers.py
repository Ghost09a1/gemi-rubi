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
        Generate the URL patterns for the router
        """
        urls = []

        for prefix, viewset, basename in self.registry:
            # Add version prefix to the URL pattern
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the URL pattern
                regex = route.url.format(
                    prefix=prefix, lookup=lookup, trailing_slash=self.trailing_slash
                )

                # Add version prefix
                regex = r"^(?P<version>v[0-9]+)/" + regex.lstrip("^")

                # Add the view
                initkwargs = route.initkwargs.copy()
                initkwargs.update(
                    {
                        "basename": basename,
                        "detail": route.detail,
                    }
                )

                view = viewset.as_view(mapping, **initkwargs)
                name = self.get_default_basename(viewset)
                if route.detail:
                    name = "{}-detail".format(name)

                urls.append(self.url(r"^{}$".format(regex), view, name=name))

        return urls
