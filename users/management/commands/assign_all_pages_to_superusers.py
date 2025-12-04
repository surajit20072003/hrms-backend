from django.core.management.base import BaseCommand
from users.models import Page, Role, User
from django.db import transaction


class Command(BaseCommand):
    help = 'Automatically assign all pages to all superuser roles'

    def handle(self, *args, **options):
        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(
                self.style.WARNING('No superusers found in the database.')
            )
            return

        # Get all pages
        all_pages = Page.objects.all()
        total_pages = all_pages.count()

        if total_pages == 0:
            self.stdout.write(
                self.style.WARNING('No pages found in the database.')
            )
            return

        updated_roles = []
        
        with transaction.atomic():
            for user in superusers:
                if user.role:
                    # Assign all pages to this superuser's role
                    user.role.pages.set(all_pages)
                    
                    # Also update group permissions
                    if user.role.group:
                        native_perms = [p.native_permission for p in all_pages if p.native_permission]
                        user.role.group.permissions.set(native_perms)
                    
                    updated_roles.append(user.role.name)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Assigned {total_pages} pages to role "{user.role.name}" (user: {user.email})'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Superuser {user.email} has no role assigned'
                        )
                    )

        if updated_roles:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully updated {len(updated_roles)} role(s): {", ".join(set(updated_roles))}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    '\nNo roles were updated. Make sure superusers have roles assigned.'
                )
            )
