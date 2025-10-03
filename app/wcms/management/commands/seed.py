from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wcms.models import Bucket, Page, Tag, Comment, Asset
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with fake data'

    def handle(self, *args, **options):
        USER_DATA = [
            {
                'email': "testuser3@gmail.com", 
                'first_name': 'John', 
                'last_name': 'Smith', 
                'bio': 'Tech writer and blogger passionate about AI and web development.', 
                'username':'2OboAl7T7zXciM8y4YM5CjunICI3',
                'pfp':'https://static.wikia.nocookie.net/shadowslave/images/8/87/Sunny_midjourney_art.png/revision/latest?cb=20231127110610'
            },
            {
                'email': 'testuser2@gmail.com', 
                'first_name': 'Ena', 
                'username': '1m1emFHVQbSybWl0nlgeo38W4ns1',
                'last_name': 'Guo', 
                'bio': 'Full-stack developer and open source contributor.',
                'pfp':'https://preview.redd.it/drop-your-best-furina-wallpaper-and-pfp-v0-g9vs3awrtt1c1.png'

            },
            {
                'email': 'testuser1@gmail.com', 
                'first_name': 'Abigail', 
                'last_name': 'Chen', 
                'username':'BWOocf2KHabqngSHxS2A6wTvTsK2',
                'bio': 'UI/UX designer with a love for minimalist interfaces.',
                'pfp':'https://preview.redd.it/lotm-general-i-had-to-im-sorry-v0-h994csv0zihf1.jpeg'
            },
        ]

        TAGS_DATA = [
            {'name': 'Technology', 'description': 'Latest trends in tech, programming, and innovation'},
            {'name': 'Travel', 'description': 'Travel guides, tips, and destination reviews'},
            {'name': 'Food', 'description': 'Recipes, restaurant reviews, and culinary experiences'},
            {'name': 'Photography', 'description': 'Photo techniques, gear reviews, and visual inspiration'},
            {'name': 'Fitness', 'description': 'Workout routines, health tips, and wellness advice'},
        ]

        BUCKET_DATA = [
            {
                'name': 'Future Light', 
                'description': 'A novel being written by this application.',
            },
            {'name': 'Wanderlust Chronicles', 'description': 'Adventures and stories from around the globe'},
            {'name': 'Culinary Creations', 'description': 'Recipes, techniques, and food photography from the kitchen'},
            {'name': 'Code & Coffee', 'description': 'Programming tutorials and development best practices'},
            {'name': 'Design Inspiration', 'description': 'Creative works and design process insights'},
            {'name': 'Art Journey', 'description': 'Art logs, style tips, and journey transformations'},
            {'name': 'Startup Stories', 'description': 'Entrepreneurial journeys and business lessons learned'},
            {'name': 'Photo Essays', 'description': 'Visual storytelling through powerful photography'},
        ]

        PAGE_TITLES = [
            'Getting Started with Machine Learning',
            'The Ultimate Guide to Remote Work',
            'Building Scalable Web Applications',
            'Street Photography in Tokyo',
            'Healthy Meal Prep for Busy Professionals',
            'Designing User-Friendly Interfaces',
            'Starting Your First Business',
            'Advanced Python Programming Techniques',
            'Travel Photography Tips for Beginners',
            'The Future of Sustainable Technology',
            'Home Workout Routines That Actually Work',
            'Creating Engaging Social Media Content',
            'Introduction to Cloud Computing',
            'Budget Travel Hacks for Students',
            'Mastering JavaScript Frameworks',
            'Portrait Photography Lighting Setup',
            'Healthy Breakfast Ideas for Weight Loss',
            'Building Your Personal Brand Online',
            'Database Design Best Practices',
            'Hidden Gems in European Cities',
        ]


        self.stdout.write('Starting to seed database...')

        # Create users
        self.stdout.write('Creating users...')
        users = []
        
        for user_blob in USER_DATA:
            user = User.objects.create_user(
                email=user_blob['email'],
                first_name=user_blob['first_name'],
                last_name=user_blob['last_name'],
                bio=user_blob['bio'],
                pfp=user_blob['pfp'],
                username=user_blob['username'],
                dictionary=random.choice(['en-US', 'en-GB']),
                theme=random.choice([True, False])
            )
            user.save()
            users.append(user)
        self.stdout.write(f'Created {len(users)} users')

        # Create tags
        self.stdout.write('Creating tags...')
        tags = []
        for tag in TAGS_DATA:
            tag = Tag.objects.create(
                tag_name=tag['name'],
                tag_description=tag['description']
            )
            tags.append(tag)
        self.stdout.write(f'Created {len(tags)} tags')

        # Create buckets
        self.stdout.write('Creating buckets...')
        buckets = []
        
        # Static banner images from Wikipedia Commons and reliable sources
        banner_images = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Good_Food_Display_-_NCI_Visuals_Online.jpg/800px-Good_Food_Display_-_NCI_Visuals_Online.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Sunset_over_the_Golden_Gate_Bridge.jpg/800px-Sunset_over_the_Golden_Gate_Bridge.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Square_200x200.png/800px-Square_200x200.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Felis_silvestris_silvestris_small_gradual_decrease_of_quality.png/800px-Felis_silvestris_silvestris_small_gradual_decrease_of_quality.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Vd-Orig.png/800px-Vd-Orig.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Ladybug_Coccinella_septempunctata.jpg/800px-Ladybug_Coccinella_septempunctata.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Anatomy_of_a_Sunset-2.jpg/800px-Anatomy_of_a_Sunset-2.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/European_Central_Bank_-_Frankfurt%2C_Germany_-_panoramio_%2810%29.jpg/800px-European_Central_Bank_-_Frankfurt%2C_Germany_-_panoramio_%2810%29.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Image_created_with_a_mobile_phone.png/800px-Image_created_with_a_mobile_phone.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Turkish_Van_Cat.jpg/800px-Turkish_Van_Cat.jpg"
        ]
        
        for bucket in BUCKET_DATA:
            bucket_owner = random.choice(buckets) if buckets and random.random() < 0.2 else None
            bucket = Bucket.objects.create(
                name=bucket['name'],
                bucket_owner=bucket_owner,
                user_owner=random.choice(users) if bucket_owner is None else bucket_owner.user_owner,
                visibility=random.choice([True, True, False]),  # 75% public
                description=bucket['description'],
                banner=random.choice(banner_images),
                background=random.choice(banner_images)
            )
            # Add 1-3 random tags to bucket
            bucket_tags = random.sample(tags, random.randint(1, min(3, len(tags))))
            bucket.tags.set(bucket_tags)
            buckets.append(bucket)
        self.stdout.write(f'Created {len(buckets)} buckets')

        # Create pages
        self.stdout.write('Creating pages...')
        pages = []
        descriptions = [
            "A comprehensive guide covering everything you need to know to get started.",
            "Learn the essential concepts and practical applications through real-world examples.",
            "Step-by-step tutorial with detailed explanations and helpful tips.",
            "In-depth analysis of best practices and common pitfalls to avoid.",
            "Practical insights from years of experience in the field.",
            "Everything you need to master this topic, from basics to advanced techniques.",
            "A detailed exploration of methods that actually work in practice.",
            "Proven strategies and actionable advice for immediate implementation.",
            "Expert tips and tricks that will save you time and effort.",
            "Complete breakdown of the process with clear, easy-to-follow instructions.",
        ]
        
        for page in PAGE_TITLES:
            bucket = random.choice(buckets)
            page = Page.objects.create(
                title=page,
                description=random.choice(descriptions),
                porder=random.randint(1,1000),
                public=random.choice([True, True, False]),  # 66% public
                bucket=bucket,
                owner=bucket.user_owner
            )
            page.save()
            pages.append(page)
        self.stdout.write(f'Created {len(pages)} pages')

        self.stdout.write(
            self.style.WARNING(
                'All users have password: asdf1234 and are authenticated through firebase.'
            )
        )
