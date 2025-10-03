from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Reset the database by dropping all tables, running migrations, and seeding data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-seed',
            action='store_true',
            help='Skip seeding the database with fake data',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of users to create when seeding (default: 5)'
        )
        parser.add_argument(
            '--tags',
            type=int,
            default=10,
            help='Number of tags to create when seeding (default: 10)'
        )
        parser.add_argument(
            '--buckets',
            type=int,
            default=15,
            help='Number of buckets to create when seeding (default: 15)'
        )
        parser.add_argument(
            '--pages',
            type=int,
            default=50,
            help='Number of pages to create when seeding (default: 50)'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=100,
            help='Number of comments to create when seeding (default: 100)'
        )
        parser.add_argument(
            '--assets',
            type=int,
            default=30,
            help='Number of assets to create when seeding (default: 30)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING('This will completely reset your database!')
        )
        self.stdout.write(
            self.style.WARNING('All existing data will be lost!')
        )
        
        # Ask for confirmation
        confirm = input('Are you sure you want to continue? (yes/no): ')
        if confirm.lower() not in ['yes', 'y']:
            self.stdout.write(self.style.SUCCESS('Operation cancelled.'))
            return

        try:
            # Step 1: Drop the database
            self.stdout.write('Step 1: Dropping database...')
            self._drop_database()
            
            # Step 2: Run migrations
            self.stdout.write('Step 2: Running migrations...')
            call_command('migrate', verbosity=0)
            
            # Step 3: Seed data (unless --no-seed is specified)
            if not options['no_seed']:
                self.stdout.write('Step 3: Seeding database...')
                seed_options = {
                    'users': options['users'],
                    'tags': options['tags'],
                    'buckets': options['buckets'],
                    'pages': options['pages'],
                    'comments': options['comments'],
                    'assets': options['assets'],
                }
                call_command('seed', **seed_options)
            else:
                self.stdout.write('Step 3: Skipping database seeding (--no-seed specified)')
                
            self.stdout.write(
                self.style.SUCCESS('Database reset completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during database reset: {str(e)}')
            )
            raise

    def _drop_database(self):
        """Drop all tables from the database"""
        db_name = settings.DATABASES['default']['NAME']
        engine = settings.DATABASES['default']['ENGINE']
        
        if 'sqlite3' in engine:
            # For SQLite, just delete the file
            if os.path.exists(db_name):
                os.remove(db_name)
                self.stdout.write(f'Deleted SQLite database file: {db_name}')
            else:
                self.stdout.write('SQLite database file does not exist, skipping deletion')
        
        elif 'postgresql' in engine:
            # For PostgreSQL
            with connection.cursor() as cursor:
                # Get all table names
                cursor.execute("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public';
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                if tables:
                    # Drop all tables with CASCADE to handle foreign keys
                    table_list = ', '.join([f'"{table}"' for table in tables])
                    cursor.execute(f'DROP TABLE {table_list} CASCADE;')
                    self.stdout.write(f'Dropped {len(tables)} tables from PostgreSQL database')
                else:
                    self.stdout.write('No tables found in PostgreSQL database')
        
        elif 'mysql' in engine:
            # For MySQL
            with connection.cursor() as cursor:
                # Disable foreign key checks temporarily
                cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
                
                # Get all table names
                cursor.execute("SHOW TABLES;")
                tables = [row[0] for row in cursor.fetchall()]
                
                if tables:
                    # Drop all tables
                    for table in tables:
                        cursor.execute(f'DROP TABLE `{table}`;')
                    self.stdout.write(f'Dropped {len(tables)} tables from MySQL database')
                else:
                    self.stdout.write('No tables found in MySQL database')
                
                # Re-enable foreign key checks
                cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
        
        else:
            # Fallback method for other databases using Django's introspection
            with connection.cursor() as cursor:
                # Get all table names using Django's introspection
                table_names = connection.introspection.table_names(cursor)
                
                if table_names:
                    # Try to drop tables (this might fail with foreign key constraints)
                    for table_name in table_names:
                        try:
                            cursor.execute(f'DROP TABLE "{table_name}" CASCADE;')
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Could not drop table {table_name}: {str(e)}'
                                )
                            )
                    self.stdout.write(f'Attempted to drop {len(table_names)} tables')
                else:
                    self.stdout.write('No tables found in database')
