# users/management/commands/seed_pages.py

from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Page, Role # Ensure Role is imported
from users.management.page_data import PAGES_DATA 
from django.contrib.auth.models import Permission 


class Command(BaseCommand):
    help = 'Seeds the database with all Page/Feature definitions required for Role Permissions.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting Page Seeding..."))

        with transaction.atomic():
            created_count = 0

            for item in PAGES_DATA:
                codename = item['codename']

                # Try to link to a native Django Permission if codename matches
                native_perm = Permission.objects.filter(codename=codename).first()

                # Create or update the Page object based on the unique 'codename'
                page, created = Page.objects.update_or_create(
                    codename=codename,
                    defaults={
                        'name': item['name'],
                        'module': item['module'],
                        'url_name': item['url_name'],
                        'native_permission': native_perm 
                    }
                )
                if created:
                    created_count += 1

            # --- Auto-Assign Pages to Default Admin/Superuser Roles (Important) ---
            all_pages = Page.objects.all()

            # Identify roles that should have full access (e.g., if you created a default 'Admin' Role)
            admin_roles = Role.objects.filter(name__in=['Admin', 'Superuser', 'Administrator'])

            for role in admin_roles:
                # Check if the role already has all pages assigned
                if role.pages.count() != all_pages.count():
                    role.pages.set(all_pages)
                    self.stdout.write(self.style.SUCCESS(f"✅ Auto-assigned ALL {all_pages.count()} pages to Admin Role: {role.name}"))

            self.stdout.write(self.style.SUCCESS(
                f"\nPage Seeding Complete. {created_count} new pages created. Total pages: {Page.objects.count()}"
            ))