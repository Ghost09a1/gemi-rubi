from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class ModeratorRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be a moderator
    """
    def test_func(self):
        """
        Check if the user is authenticated and a moderator
        """
        return self.request.user.is_authenticated and self.request.user.groups.filter(name='Moderators').exists()

    def handle_no_permission(self):
        """
        Handle the case where the user is not a moderator
        """
        messages.error(self.request, _("You do not have permission to access this page."))
        return redirect('accounts:profile_detail', username=self.request.user.username)


class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin that requires the user to be an admin (superuser)
    """
    def test_func(self):
        """
        Check if the user is authenticated and a superuser
        """
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        """
        Handle the case where the user is not an admin
        """
        messages.error(self.request, _("This feature requires administrator privileges."))
        return redirect('accounts:profile_detail', username=self.request.user.username)
