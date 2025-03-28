"""Copyright 2025  Place au Vélo."""

from django.conf import settings


def role(request):
    """Provide template access to our role.

    The settings_local.py must define a role.  Make sure it's provided
    in the context, as well as a boolean for whether or not we're
    running in production.

    This function is configured to be used via the TEMPLATES setting
    (-> OPTIONS -> context_processors).

    """
    if hasattr(settings, "ROLE"):
        role = settings.ROLE
    else:
        role = "unknown"
    if "production" == role:
        is_prod = True
    else:
        is_prod = False
    return {"role": role, "is_production": is_prod}
