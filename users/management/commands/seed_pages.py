from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Page, Role
from users.management.page_data import PAGES_DATA
from django.contrib.auth.models import Permission

class Command(BaseCommand):
    help = "Seed pages (two-pass) with parent/module_order/order."

    def handle(self, *args, **options):
        self.stdout.write("Starting seed pages...")
        with transaction.atomic():
            # pass 1: create/update pages without parent set
            created = 0
            updated = 0
            codename_to_page = {}

            for item in PAGES_DATA:
                codename = item['codename']
                module = item.get('module')
                page_icon = item.get('module_icon', 'list_alt')
                native_perm = Permission.objects.filter(codename=codename).first()

                defaults = {
                    'name': item['name'],
                    'module': module,
                    'url_name': item.get('url_name'),
                    'module_icon': page_icon,
                    'native_permission': native_perm,
                    'module_order': item.get('module_order', 999),
                    'order': item.get('order', 999)
                }

                # parent left out for now
                page, created_flag = Page.objects.update_or_create(codename=codename, defaults=defaults)
                if created_flag:
                    created += 1
                else:
                    updated += 1
                codename_to_page[codename] = page

            # pass 2: set parents using parent_codename
            parent_updates = 0
            for item in PAGES_DATA:
                codename = item['codename']
                parent_codename = item.get('parent_codename')
                if parent_codename:
                    page = codename_to_page[codename]
                    parent_page = codename_to_page.get(parent_codename) or Page.objects.filter(codename=parent_codename).first()
                    if parent_page and page.parent_id != parent_page.id:
                        page.parent = parent_page
                        page.save(update_fields=['parent'])
                        parent_updates += 1

            # optionally auto-assign pages to admin roles
            all_pages = Page.objects.all()
            admin_roles = Role.objects.filter(name__in=['Admin','Administrator','Superuser'])
            for role in admin_roles:
                role.pages.set(all_pages)

            self.stdout.write(self.style.SUCCESS(
                f"Done. created={created}, updated={updated}, parents_set={parent_updates}"
            ))
