import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedUUIDModel


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier for authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_verified", False)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using UUID primary key and email address as unique authentication identifier.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, db_index=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="First Name")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Last Name")
    is_active = models.BooleanField(default=True, verbose_name="Active Status")
    is_staff = models.BooleanField(default=False, verbose_name="Staff Status")
    is_superuser = models.BooleanField(default=False, verbose_name="Superuser Status")
    is_verified = models.BooleanField(default=False, verbose_name="Verified Status")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Date Joined")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Last Login")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def get_short_name(self):
        return self.first_name if self.first_name else self.email

    @property
    def roles(self):
        return Role.objects.filter(role_users__user=self)

    def has_role(self, role_code):
        return self.user_roles.filter(role__code=role_code).exists()


class UserProfile(TimeStampedUUIDModel):
    """
    User Profile model containing extensible student biographical and demographic information.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="User",
    )
    target_exam = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Target Exam",
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Phone Number",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="Avatar Image",
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bio",
    )

    class Meta:
        db_table = "user_profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile of {self.user.email}"


class Role(TimeStampedUUIDModel):
    """
    RBAC Role model defining system operational roles.
    Standard roles: STUDENT, CONTENT_EDITOR, SME, SUPPORT_AGENT, ADMIN, SUPERADMIN
    """
    name = models.CharField(max_length=100, verbose_name="Role Name")
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Role Code",
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Permission(TimeStampedUUIDModel):
    """
    RBAC Permission model defining atomic system capability rights.
    """
    name = models.CharField(max_length=100, verbose_name="Permission Name")
    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Permission Code",
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    class Meta:
        db_table = "permissions"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class RolePermission(models.Model):
    """
    Junction model connecting permissions to RBAC roles.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
        verbose_name="Role",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="permission_roles",
        verbose_name="Permission",
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")

    class Meta:
        db_table = "role_permissions"
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.code} -> {self.permission.code}"


class UserRole(models.Model):
    """
    Junction model assigning RBAC roles to users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="User",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_users",
        verbose_name="Role",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_user_roles",
        verbose_name="Assigned By",
    )
    assigned_at = models.DateTimeField(default=timezone.now, verbose_name="Assigned At")

    class Meta:
        db_table = "user_roles"
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user.email} -> {self.role.code}"
