from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase

from apps.accounts.models import Permission, Role, RolePermission, UserRole

User = get_user_model()


class RBACTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="rbac_user@prepora.com",
            password="SecurePassword123!",
            first_name="RBAC",
            last_name="User",
        )

    def test_role_creation(self):
        """
        1. Test role creation.
        """
        role = Role.objects.create(
            name="Test Role",
            code="TEST_ROLE",
            description="Test role description",
        )
        self.assertIsNotNone(role.id)
        self.assertEqual(role.code, "TEST_ROLE")
        self.assertEqual(str(role), "Test Role (TEST_ROLE)")

    def test_permission_creation(self):
        """
        2. Test permission creation.
        """
        perm = Permission.objects.create(
            name="Test Permission",
            code="test.permission",
            description="Test permission description",
        )
        self.assertIsNotNone(perm.id)
        self.assertEqual(perm.code, "test.permission")
        self.assertEqual(str(perm), "Test Permission (test.permission)")

    def test_role_permission_relationship(self):
        """
        3. Test RolePermission relationship.
        """
        role = Role.objects.create(name="Editor", code="EDITOR")
        perm = Permission.objects.create(name="Edit Notes", code="notes.edit")
        rp = RolePermission.objects.create(role=role, permission=perm)

        self.assertEqual(rp.role, role)
        self.assertEqual(rp.permission, perm)
        self.assertEqual(str(rp), "EDITOR -> notes.edit")

    def test_user_role_relationship(self):
        """
        4. Test UserRole relationship.
        """
        role = Role.objects.create(name="Student", code="STUDENT")
        ur = UserRole.objects.create(user=self.user, role=role)

        self.assertEqual(ur.user, self.user)
        self.assertEqual(ur.role, role)
        self.assertTrue(self.user.has_role("STUDENT"))
        self.assertIn(role, self.user.roles)
        self.assertEqual(str(ur), f"{self.user.email} -> STUDENT")

    def test_duplicate_role_permission_prevented(self):
        """
        5. Test duplicate RolePermission is prevented by unique constraint.
        """
        role = Role.objects.create(name="Admin", code="ADMIN_TEST")
        perm = Permission.objects.create(name="Manage", code="manage.all")
        RolePermission.objects.create(role=role, permission=perm)

        with self.assertRaises(IntegrityError):
            RolePermission.objects.create(role=role, permission=perm)

    def test_duplicate_user_role_prevented(self):
        """
        6. Test duplicate UserRole is prevented by unique constraint.
        """
        role = Role.objects.create(name="SME", code="SME_TEST")
        UserRole.objects.create(user=self.user, role=role)

        with self.assertRaises(IntegrityError):
            UserRole.objects.create(user=self.user, role=role)

    def test_role_code_uniqueness(self):
        """
        7. Test role code uniqueness.
        """
        Role.objects.create(name="Unique Role 1", code="UNIQUE_CODE")
        with self.assertRaises(IntegrityError):
            Role.objects.create(name="Unique Role 2", code="UNIQUE_CODE")

    def test_permission_code_uniqueness(self):
        """
        8. Test permission code uniqueness.
        """
        Permission.objects.create(name="Unique Perm 1", code="unique.perm")
        with self.assertRaises(IntegrityError):
            Permission.objects.create(name="Unique Perm 2", code="unique.perm")

    def test_seed_roles_creates_all_six_roles(self):
        """
        9. Test seed_roles command creates all six standard roles.
        """
        call_command("seed_roles")
        expected_codes = {
            "STUDENT",
            "CONTENT_EDITOR",
            "SME",
            "SUPPORT_AGENT",
            "ADMIN",
            "SUPERADMIN",
        }
        db_codes = set(Role.objects.values_list("code", flat=True))
        self.assertTrue(expected_codes.issubset(db_codes))

    def test_seed_roles_idempotency(self):
        """
        10. Test running seed_roles twice is idempotent.
        """
        call_command("seed_roles")
        initial_roles_count = Role.objects.count()
        initial_perms_count = Permission.objects.count()
        initial_mappings_count = RolePermission.objects.count()

        # Run a second time
        call_command("seed_roles")
        self.assertEqual(Role.objects.count(), initial_roles_count)
        self.assertEqual(Permission.objects.count(), initial_perms_count)
        self.assertEqual(RolePermission.objects.count(), initial_mappings_count)

    def test_initial_permissions_created(self):
        """
        11. Test initial permissions are created by seed_roles.
        """
        call_command("seed_roles")
        expected_perm_codes = {
            "users.view",
            "users.manage",
            "profiles.view",
            "profiles.manage",
            "content.manage",
            "content.review",
            "admin.manage",
        }
        db_perm_codes = set(Permission.objects.values_list("code", flat=True))
        self.assertTrue(expected_perm_codes.issubset(db_perm_codes))

    def test_role_permission_mappings_created(self):
        """
        12. Test role-permission mappings are assigned accurately by seed_roles.
        """
        call_command("seed_roles")

        student_role = Role.objects.get(code="STUDENT")
        student_perms = set(
            RolePermission.objects.filter(role=student_role).values_list(
                "permission__code", flat=True
            )
        )
        self.assertEqual(student_perms, {"profiles.view", "profiles.manage"})

        superadmin_role = Role.objects.get(code="SUPERADMIN")
        superadmin_perms = set(
            RolePermission.objects.filter(role=superadmin_role).values_list(
                "permission__code", flat=True
            )
        )
        self.assertEqual(len(superadmin_perms), 7)
