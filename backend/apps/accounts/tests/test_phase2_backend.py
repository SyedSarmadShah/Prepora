from datetime import timedelta
import uuid

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone
from rest_framework.views import APIView

from apps.accounts.models import AuditLog, RefreshToken, Role, UserProfile, UserRole
from apps.accounts.permissions import HasRole

User = get_user_model()


class Phase2BackendRequirementsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Users
        self.student_user = User.objects.create_user(
            email="student_test@prepora.com",
            password="SecurePassword123!",
            first_name="Student",
            last_name="User",
        )
        self.admin_user = User.objects.create_user(
            email="admin_test@prepora.com",
            password="SecurePassword123!",
            first_name="Admin",
            last_name="User",
        )

        # Roles
        self.student_role = Role.objects.create(name="Student", code="STUDENT")
        self.admin_role = Role.objects.create(name="Administrator", code="ADMIN")

        # Assign roles
        UserRole.objects.create(user=self.student_user, role=self.student_role)
        UserRole.objects.create(user=self.admin_user, role=self.admin_role)

    def test_has_role_permission_unauthenticated(self):
        """
        HasRole permission class should reject unauthenticated requests.
        """
        request = self.factory.get("/api/v1/admin/test/")
        request.user = None

        permission = HasRole(["ADMIN"])
        self.assertFalse(permission.has_permission(request, None))

    def test_has_role_permission_unauthorized_role(self):
        """
        HasRole permission class should reject authenticated user lacking the required role.
        """
        request = self.factory.get("/api/v1/admin/test/")
        request.user = self.student_user

        permission = HasRole(["ADMIN"])
        self.assertFalse(permission.has_permission(request, None))

    def test_has_role_permission_authorized_role(self):
        """
        HasRole permission class should grant access to authenticated user with required role.
        """
        request = self.factory.get("/api/v1/admin/test/")
        request.user = self.admin_user

        permission = HasRole(["ADMIN"])
        self.assertTrue(permission.has_permission(request, None))

    def test_has_role_factory_with_roles(self):
        """
        HasRole.with_roles("ADMIN", "SUPERADMIN") factory syntax works properly.
        """
        permission_class = HasRole.with_roles("ADMIN", "SUPERADMIN")
        permission = permission_class()

        request = self.factory.get("/api/v1/admin/test/")
        request.user = self.admin_user

        class DummyView(APIView):
            pass

        self.assertTrue(permission.has_permission(request, DummyView()))

    def test_refresh_token_model_creation_and_lookup(self):
        """
        RefreshToken model creation, attributes, and index lookup.
        """
        token_str = "sample.refresh.token.hash.value"
        expires = timezone.now() + timedelta(days=7)

        token_obj = RefreshToken.objects.create(
            user=self.student_user,
            token=token_str,
            device_info="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            ip_address="127.0.0.1",
            expires_at=expires,
        )

        self.assertIsNotNone(token_obj.id)
        self.assertEqual(token_obj.user, self.student_user)
        self.assertFalse(token_obj.is_revoked)

        # Lookup using indexing pattern
        found = RefreshToken.objects.filter(
            user=self.student_user,
            is_revoked=False,
            expires_at__gt=timezone.now(),
        ).first()

        self.assertEqual(found, token_obj)

    def test_audit_log_model_creation(self):
        """
        AuditLog model creation and fields verification.
        """
        target_uuid = uuid.uuid4()
        audit_entry = AuditLog.objects.create(
            actor=self.admin_user,
            action="USER_ROLE_ASSIGNED",
            target_entity_type="UserRole",
            target_entity_id=target_uuid,
            ip_address="192.168.1.1",
            pre_change_state={"roles": []},
            post_change_state={"roles": ["ADMIN"]},
        )

        self.assertIsNotNone(audit_entry.id)
        self.assertEqual(audit_entry.actor, self.admin_user)
        self.assertEqual(audit_entry.action, "USER_ROLE_ASSIGNED")
        self.assertEqual(audit_entry.target_entity_id, target_uuid)
        self.assertEqual(
            str(audit_entry),
            f"AuditLog(USER_ROLE_ASSIGNED by {self.admin_user.email})",
        )

    def test_post_save_signal_creates_user_profile(self):
        """
        Creating a User triggers post_save signal auto-creating a UserProfile.
        """
        new_user = User.objects.create_user(
            email="signal_user@prepora.com",
            password="SecurePassword123!",
        )

        # Check profile exists
        profile = UserProfile.objects.filter(user=new_user).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, new_user)

    def test_database_indexes_exist_in_meta(self):
        """
        Verify database indexes idx_users_email_lower and idx_refresh_tokens_lookup are configured.
        """
        user_index_names = [idx.name for idx in User._meta.indexes]
        self.assertIn("idx_users_email_lower", user_index_names)

        refresh_index_names = [idx.name for idx in RefreshToken._meta.indexes]
        self.assertIn("idx_refresh_tokens_lookup", refresh_index_names)
