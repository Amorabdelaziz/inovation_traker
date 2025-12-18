# Save this file in your project root directory
# Run it with: python manage.py shell < populate_categories.py

from ideas.models import Category

# Create default categories
categories_data = [
    {
        'name': 'Technology',
        'description': 'Innovative technology solutions and digital transformation'
    },
    {
        'name': 'Process Improvement',
        'description': 'Ideas to improve business processes and workflows'
    },
    {
        'name': 'Customer Experience',
        'description': 'Innovations to enhance customer satisfaction and engagement'
    },
    {
        'name': 'Product Development',
        'description': 'New product ideas and enhancements'
    },
    {
        'name': 'Sustainability',
        'description': 'Eco-friendly and sustainable innovation ideas'
    },
    {
        'name': 'Education',
        'description': 'Educational innovations and learning improvements'
    },
    {
        'name': 'Other',
        'description': 'Other innovative ideas that don\'t fit specific categories'
    }
]

# Add categories to database
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"✓ Created category: {category.name}")
    else:
        print(f"• Category already exists: {category.name}")

print("\nCategories setup complete!")