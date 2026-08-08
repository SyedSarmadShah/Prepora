from django.core.management.base import BaseCommand
from apps.accounts.models import Permission, Role, RolePermission


class Command(BaseCommand):
    help = "Seeds initial system RBAC roles, permissions, and role-permission mappings."

    def handle(self, *args, **options):
        # 1. Define initial permissions catalog
        permissions_data = [
            {
                "code": "users.view",
                "name": "View Users",
                "description": "View user accounts and basic details",
            },
            {
                "code": "users.manage",
                "name": "Manage Users",
                "description": "Create, update, or deactivate user accounts",
            },
            {
                "code": "profiles.view",
                "name": "View Profiles",
                "description": "View student profile details",
            },
            {
                "code": "profiles.manage",
                "name": "Manage Profiles",
                "description": "Edit or update user profiles",
            },
            {
                "code": "content.manage",
                "name": "Manage Content",
                "description": "Create, edit, and update educational content",
            },
            {
                "code": "content.review",
                "name": "Review Content",
                "description": "Review and approve authored content",
            },
            {
                "code": "admin.manage",
                "name": "Administrative Management",
                "description": "Full platform administrative access",
            },
        ]

        created_perms = 0
        perm_objects = {}
        for item in permissions_data:
            perm, created = Permission.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                },
            )
            perm_objects[item["code"]] = perm
            if created:
                created_perms += 1

        # 2. Define standard system roles and permission assignments
        roles_data = [
            {
                "code": "STUDENT",
                "name": "Student",
                "description": "Standard student learner account",
                "permissions": ["profiles.view", "profiles.manage"],
            },
            {
                "code": "CONTENT_EDITOR",
                "name": "Content Editor",
                "description": "Author and editor of educational question bank & notes",
                "permissions": ["profiles.view", "profiles.manage", "content.manage"],
            },
            {
                "code": "SME",
                "name": "Subject Matter Expert",
                "description": "Subject matter expert for reviewing and approving content",
                "permissions": [
                    "profiles.view",
                    "profiles.manage",
                    "content.manage",
                    "content.review",
                ],
            },
            {
                "code": "SUPPORT_AGENT",
                "name": "Support Agent",
                "description": "Customer support agent for managing student accounts and profiles",
                "permissions": ["users.view", "profiles.view", "profiles.manage"],
            },
            {
                "code": "ADMIN",
                "name": "Administrator",
                "description": "Platform administrator with broad operational capabilities",
                "permissions": [
                    "users.view",
                    "users.manage",
                    "profiles.view",
                    "profiles.manage",
                    "content.manage",
                    "content.review",
                    "admin.manage",
                ],
            },
            {
                "code": "SUPERADMIN",
                "name": "Super Administrator",
                "description": "Super administrator with complete system access and security oversight",
                "permissions": [
                    "users.view",
                    "users.manage",
                    "profiles.view",
                    "profiles.manage",
                    "content.manage",
                    "content.review",
                    "admin.manage",
                ],
            },
        ]

        created_roles = 0
        created_mappings = 0

        for item in roles_data:
            role, created = Role.objects.update_or_create(
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                },
            )
            if created:
                created_roles += 1

            for perm_code in item["permissions"]:
                perm = perm_objects[perm_code]
                _, map_created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=perm,
                )
                if map_created:
                    created_mappings += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded RBAC foundation: {created_roles} roles created, "
                f"{created_perms} permissions created, {created_mappings} role-permission mappings created."
            )
        )
