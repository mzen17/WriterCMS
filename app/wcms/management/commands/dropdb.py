from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Drop all tables from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        if not options['force']:
            self.stdout.write(
                self.style.WARNING('This will drop all tables from your database!')
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
            self.stdout.write('Dropping database...')
            self._drop_database()
            self.stdout.write(
                self.style.SUCCESS('Database dropped successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during database drop: {str(e)}')
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
                self.stdout.write('SQLite database file does not exist, already dropped')
        
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
