from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance, created, **kwargs):
    """
    Signal handler running post-creation of User:
    1. Automatically creates associated UserProfile if not already existing.
    2. Safely binds default FREE subscription tier if Subscription model is active (Phase 8 compatibility).
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)

        try:
            from apps.subscriptions.models import Subscription, SubscriptionPlan

            free_plan, _ = SubscriptionPlan.objects.get_or_create(
                code="FREE",
                defaults={"title": "Free Plan", "price_amount": 0, "currency": "PKR"},
            )
            Subscription.objects.get_or_create(
                user=instance,
                defaults={"subscription_plan": free_plan, "status": "ACTIVE"},
            )
        except (ImportError, Exception):
            pass
