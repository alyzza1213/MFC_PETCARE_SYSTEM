from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'


    def ready(self):
        from django.contrib.auth.models import User

        # --- Ensure LeanneJane exists ---
        try:
            user = User.objects.get(username='LeanneJane')
            user.set_password('jane12345')
            user.is_active = True
            user.save()
            print("LeanneJane password updated successfully!")
        except User.DoesNotExist:
            User.objects.create_user(
                username='LeanneJane',
                password='jane12345',
                is_active=True
            )
            print("LeanneJane user created successfully!")

        # --- Print all registered users ---
        print("===== Registered Users =====")
        for u in User.objects.all():
            print(f"Username: {u.username}, Email: {u.email}, Superuser: {u.is_superuser}, Staff: {u.is_staff}")