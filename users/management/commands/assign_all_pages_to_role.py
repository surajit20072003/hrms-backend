from django.core.management.base import BaseCommand
from users.models import Page, Role
from django.db import transaction


class Command(BaseCommand):
    help = 'Assign all pages to a specific role (e.g., Admin, Superuser)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--role-name',
            type=str,
            help='Name of the role to assign all pages to (e.g., "Admin")',
            required=True
        )

    def handle(self, *args, **options):
        role_name = options['role_name']
        
        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Role "{role_name}" does not exist.')
            )
            self.stdout.write(
                self.style.WARNING('Available roles:')
            )
            for r in Role.objects.all():
                self.stdout.write(f'  - {r.name}')
            return

        # Get all pages
        all_pages = Page.objects.all()
        total_pages = all_pages.count()

        if total_pages == 0:
            self.stdout.write(
                self.style.WARNING('No pages found in the database.')
            )
            return

        # Assign all pages to the role
        with transaction.atomic():
            role.pages.set(all_pages)
            
            # Also update the group permissions if needed
            if role.group:
                native_perms = [p.native_permission for p in all_pages if p.native_permission]
                role.group.permissions.set(native_perms)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully assigned {total_pages} pages to role "{role_name}"'
            )
        )
        
        # Show summary
        self.stdout.write('\nAssigned pages:')
        for page in all_pages.order_by('module', 'name')[:10]:
            self.stdout.write(f'  - {page.module}: {page.name}')
        
        if total_pages > 10:
            self.stdout.write(f'  ... and {total_pages - 10} more pages')
