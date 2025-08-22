from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

class Command(BaseCommand):
    help = 'Clean up users and prepare for Firebase-only authentication'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--remove-no-firebase',
            action='store_true',
            help='Remove users that do not have a Firebase UID',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Find users without Firebase UID
        users_without_firebase = User.objects.filter(firebase_uid__isnull=True)
        users_with_firebase = User.objects.filter(firebase_uid__isnull=False)
        
        self.stdout.write(f"Users with Firebase UID: {users_with_firebase.count()}")
        self.stdout.write(f"Users without Firebase UID: {users_without_firebase.count()}")
        
        if users_without_firebase.exists():
            self.stdout.write("\nUsers without Firebase UID:")
            for user in users_without_firebase:
                self.stdout.write(f"  - {user.username} (ID: {user.id}, Email: {user.email})")
        
        if options['remove_no_firebase']:
            if options['dry_run']:
                self.stdout.write(f"\n[DRY RUN] Would remove {users_without_firebase.count()} users without Firebase UID")
            else:
                with transaction.atomic():
                    deleted_count = users_without_firebase.count()
                    users_without_firebase.delete()
                    self.stdout.write(
                        self.style.WARNING(f"Removed {deleted_count} users without Firebase UID")
                    )
        
        # Check for duplicate Firebase UIDs (shouldn't happen but good to verify)
        from django.db.models import Count
        duplicate_uids = (User.objects
                         .values('firebase_uid')
                         .annotate(count=Count('firebase_uid'))
                         .filter(count__gt=1, firebase_uid__isnull=False))
        
        if duplicate_uids:
            self.stdout.write(self.style.ERROR("\nWARNING: Found duplicate Firebase UIDs:"))
            for item in duplicate_uids:
                users = User.objects.filter(firebase_uid=item['firebase_uid'])
                self.stdout.write(f"  Firebase UID: {item['firebase_uid']}")
                for user in users:
                    self.stdout.write(f"    - {user.username} (ID: {user.id})")
        
        self.stdout.write("\nFirebase authentication migration status complete.")
