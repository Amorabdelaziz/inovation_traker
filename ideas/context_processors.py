from django.core.exceptions import ObjectDoesNotExist

from .models import UserProfile


def role_flags(request):
    user = request.user
    can_review = False
    user_role = None

    if user.is_authenticated:
        try:
            profile = user.profile
        except ObjectDoesNotExist:
            profile = None

        if profile is None and user.is_staff:
            profile, _ = UserProfile.objects.get_or_create(
                user=user, defaults={'role': UserProfile.ROLE_ADMIN}
            )

        if profile:
            user_role = profile.role
            can_review = profile.can_review

    return {
        'can_review': can_review,
        'user_role': user_role,
    }

