# users/management/commands/seed_pages.py

from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Page
from users.management.page_data import PAGES_DATA
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = "RESET and Seed Page Table with Correct Icons"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("⚠️ Deleting existing Page records..."))

        with transaction.atomic():

            # Step 1: Clear table
            Page.objects.all().delete()

            self.stdout.write(self.style.SUCCESS("🗑️ Old pages deleted.\n"))

            created_count = 0

            # Store first icon used by each module
            module_icon_cache = {}

            for item in PAGES_DATA:

                module = item["module"]

                # Pick module icon if exist, else use previous saved icon
                if "module_icon" in item:
                    module_icon_cache[module] = item["module_icon"]

                module_icon = module_icon_cache.get(module, "list_alt")  # fallback

                # Try matching native django permission
                native_permission = Permission.objects.filter(codename=item['codename']).first()

                Page.objects.create(
                    module=module,
                    name=item["name"],
                    codename=item["codename"],
                    url_name=item["url_name"],
                    module_icon=module_icon,
                    native_permission=native_permission
                )

                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n🎯 Seeding Complete: {created_count} pages created successfully.\n"
        ))

