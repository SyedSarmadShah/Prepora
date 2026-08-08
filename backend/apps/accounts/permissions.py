from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Custom DRF permission class verifying that the authenticated user possesses
    one or more required RBAC roles.

    Usage options:
    1. On class-based views: Set `permission_classes = [HasRole]` and `required_roles = ["ADMIN", "SUPERADMIN"]`.
    2. Factory syntax: `permission_classes = [HasRole.with_roles("ADMIN", "SUPERADMIN")]`.
    3. Direct instantiation in custom permission checks: `HasRole(["ADMIN"])(request, view)`.
    """

    required_roles = []

    def __init__(self, required_roles=None):
        if required_roles is not None:
            self.required_roles = required_roles

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        allowed_roles = getattr(view, "required_roles", self.required_roles)
        if not allowed_roles:
            return True

        user_role_codes = set(request.user.user_roles.values_list("role__code", flat=True))
        return any(role in user_role_codes for role in allowed_roles)

    @classmethod
    def with_roles(cls, *roles):
        """
        Factory class method returning a subclass of HasRole pre-configured with required roles.
        """

        class ConfiguredHasRole(cls):
            required_roles = list(roles)

        return ConfiguredHasRole
