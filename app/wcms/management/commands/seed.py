from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wcms.models import Bucket, Page, Tag, Comment, Asset
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with fake data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')
        parser.add_argument('--tags', type=int, default=10, help='Number of tags to create')
        parser.add_argument('--buckets', type=int, default=15, help='Number of buckets to create')
        parser.add_argument('--pages', type=int, default=50, help='Number of pages to create')
        parser.add_argument('--comments', type=int, default=100, help='Number of comments to create')
        parser.add_argument('--assets', type=int, default=30, help='Number of assets to create')

    def handle(self, *args, **options):
        # Sample data
        USERS_DATA = [
            {'username': 'john_writer', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Smith', 'bio': 'Tech writer and blogger passionate about AI and web development.'},
            {'username': 'sarah_dev', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Johnson', 'bio': 'Full-stack developer and open source contributor.'},
            {'username': 'mike_designer', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Chen', 'bio': 'UI/UX designer with a love for minimalist interfaces.'},
            {'username': 'emma_content', 'email': 'emma@example.com', 'first_name': 'Emma', 'last_name': 'Davis', 'bio': 'Content creator and digital marketing specialist.'},
            {'username': 'alex_photo', 'email': 'alex@example.com', 'first_name': 'Alex', 'last_name': 'Rodriguez', 'bio': 'Professional photographer and visual storyteller.'},
            {'username': 'lisa_travel', 'email': 'lisa@example.com', 'first_name': 'Lisa', 'last_name': 'Wilson', 'bio': 'Travel blogger exploring hidden gems around the world.'},
            {'username': 'david_chef', 'email': 'david@example.com', 'first_name': 'David', 'last_name': 'Brown', 'bio': 'Professional chef sharing culinary adventures and recipes.'},
            {'username': 'anna_fitness', 'email': 'anna@example.com', 'first_name': 'Anna', 'last_name': 'Taylor', 'bio': 'Fitness trainer and wellness coach inspiring healthy lifestyles.'},
        ]

        TAGS_DATA = [
            {'name': 'Technology', 'description': 'Latest trends in tech, programming, and innovation'},
            {'name': 'Travel', 'description': 'Travel guides, tips, and destination reviews'},
            {'name': 'Food', 'description': 'Recipes, restaurant reviews, and culinary experiences'},
            {'name': 'Photography', 'description': 'Photo techniques, gear reviews, and visual inspiration'},
            {'name': 'Fitness', 'description': 'Workout routines, health tips, and wellness advice'},
            {'name': 'Design', 'description': 'UI/UX design, graphic design, and creative inspiration'},
            {'name': 'Business', 'description': 'Entrepreneurship, startups, and business strategies'},
            {'name': 'Lifestyle', 'description': 'Daily life, productivity, and personal development'},
            {'name': 'Education', 'description': 'Learning resources, tutorials, and academic content'},
            {'name': 'Entertainment', 'description': 'Movies, games, music, and pop culture'},
        ]

        BUCKET_DATA = [
            {'name': 'Tech Insights', 'description': 'Deep dives into emerging technologies and their impact on society'},
            {'name': 'Wanderlust Chronicles', 'description': 'Adventures and stories from around the globe'},
            {'name': 'Culinary Creations', 'description': 'Recipes, techniques, and food photography from the kitchen'},
            {'name': 'Code & Coffee', 'description': 'Programming tutorials and development best practices'},
            {'name': 'Design Inspiration', 'description': 'Creative works and design process insights'},
            {'name': 'Fitness Journey', 'description': 'Workout logs, nutrition tips, and health transformations'},
            {'name': 'Startup Stories', 'description': 'Entrepreneurial journeys and business lessons learned'},
            {'name': 'Photo Essays', 'description': 'Visual storytelling through powerful photography'},
            {'name': 'Learning Lab', 'description': 'Educational content and tutorial series'},
            {'name': 'Digital Nomad Life', 'description': 'Remote work tips and location-independent lifestyle'},
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

        COMMENTS_DATA = [
            "Great article! This really helped me understand the concept better.",
            "Thanks for sharing this. I've been looking for exactly this information.",
            "Excellent tutorial. The step-by-step approach made it easy to follow.",
            "This is incredibly useful. Bookmarking for future reference!",
            "Well written and informative. Looking forward to more content like this.",
            "Amazing photos! What camera settings did you use for these shots?",
            "This recipe turned out perfect. My family loved it!",
            "Super helpful tips. I'm definitely going to try these techniques.",
            "Clear explanations and practical examples. Really appreciate the effort.",
            "Inspiring content! This motivated me to start my own project.",
            "Love the detailed breakdown. Makes complex topics accessible.",
            "Fantastic guide. Wish I had found this earlier in my journey.",
            "Your writing style is engaging and easy to understand.",
            "Practical advice that I can implement right away. Thank you!",
            "Beautiful work! The attention to detail really shows.",
        ]

        self.stdout.write('Starting to seed database...')

        # Create users
        self.stdout.write('Creating users...')
        users = []
        # Static profile pictures from Wikipedia Commons
        profile_pics = [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/User_icon_2.svg/200px-User_icon_2.svg.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Profile_avatar_placeholder_large.png/200px-Profile_avatar_placeholder_large.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Sample_User_Icon.png/200px-Sample_User_Icon.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Portrait_Placeholder.png/200px-Portrait_Placeholder.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Default_pfp.jpg/200px-Default_pfp.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Default_pfp.svg/200px-Default_pfp.svg.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Unknown_person.jpg/200px-Unknown_person.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/User_Circle.png/200px-User_Circle.png"
        ]
        for i in range(min(options['users'], len(USERS_DATA))):
            user_data = USERS_DATA[i]
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                bio=user_data['bio'],
                pfp=profile_pics[i % len(profile_pics)],
                dictionary=random.choice(['en-US', 'en-GB']),
                theme=random.choice([True, False])
            )
            user.set_password('password123')
            user.save()
            users.append(user)
        self.stdout.write(f'Created {len(users)} users')

        # Create tags
        self.stdout.write('Creating tags...')
        tags = []
        for i in range(min(options['tags'], len(TAGS_DATA))):
            tag_data = TAGS_DATA[i]
            tag = Tag.objects.create(
                tag_name=tag_data['name'],
                tag_description=tag_data['description']
            )
            tags.append(tag)
        self.stdout.write(f'Created {len(tags)} tags')

        # Create buckets
        self.stdout.write('Creating buckets...')
        buckets = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        
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
        
        for i in range(min(options['buckets'], len(BUCKET_DATA))):
            bucket_data = BUCKET_DATA[i]
            bucket = Bucket.objects.create(
                name=bucket_data['name'],
                user_owner=users[i % len(users)],
                bucket_owner=random.choice(buckets) if buckets and random.random() < 0.2 else None,
                visibility=random.choice([True, True, True, False]),  # 75% public
                description=bucket_data['description'],
                banner=banner_images[i % len(banner_images)],
                background=colors[i % len(colors)]
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
        
        for i in range(options['pages']):
            bucket = buckets[i % len(buckets)]
            page = Page.objects.create(
                title=PAGE_TITLES[i % len(PAGE_TITLES)],
                description=descriptions[i % len(descriptions)],
                porder=i + 1,
                public=random.choice([True, True, False]),  # 66% public
                bucket=bucket,
                owner=bucket.user_owner
            )
            pages.append(page)
        self.stdout.write(f'Created {len(pages)} pages')

        # Create comments
        self.stdout.write('Creating comments...')
        comments = []
        for i in range(options['comments']):
            comment = Comment.objects.create(
                text_content=COMMENTS_DATA[i % len(COMMENTS_DATA)],
                user=random.choice(users),
                page=random.choice(pages)
            )
            comments.append(comment)
        self.stdout.write(f'Created {len(comments)} comments')

        # Create assets
        self.stdout.write('Creating assets...')
        assets = []
        asset_files = [
            {'name': 'hero-image.jpg', 'size': 1024000},
            {'name': 'tutorial-screenshot.png', 'size': 512000},
            {'name': 'presentation.pdf', 'size': 2048000},
            {'name': 'code-example.txt', 'size': 8192},
            {'name': 'data-visualization.svg', 'size': 64000},
            {'name': 'profile-photo.jpg', 'size': 256000},
            {'name': 'workflow-diagram.png', 'size': 128000},
            {'name': 'reference-document.docx', 'size': 512000},
            {'name': 'audio-interview.mp3', 'size': 8192000},
            {'name': 'demo-video.mp4', 'size': 16384000},
        ]
        
        for i in range(options['assets']):
            asset_data = asset_files[i % len(asset_files)]
            asset = Asset.objects.create(
                file_name=asset_data['name'],
                size=asset_data['size'] + random.randint(-10000, 10000),
                page=random.choice(pages)
            )
            assets.append(asset)
        self.stdout.write(f'Created {len(assets)} assets')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'  - {len(users)} users\n'
                f'  - {len(tags)} tags\n'
                f'  - {len(buckets)} buckets\n'
                f'  - {len(pages)} pages\n'
                f'  - {len(comments)} comments\n'
                f'  - {len(assets)} assets'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'All users have password: password123'
            )
        )
