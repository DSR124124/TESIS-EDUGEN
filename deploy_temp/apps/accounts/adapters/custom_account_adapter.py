# apps/accounts/adapters/custom_account_adapter.py
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.role = user.STUDENT  # Por defecto, los nuevos usuarios son estudiantes
        if commit:
            user.save()
        return user