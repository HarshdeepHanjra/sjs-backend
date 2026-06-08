# save as fix_internship_urls.py
from app import create_app, db
from app.models.internship import InternshipOrder

def fix_internship_screenshot_urls():
    """Fix existing internship payment screenshot URLs"""
    
    app = create_app()
    with app.app_context():
        # Find all internship orders with screenshot_url
        internship_orders = InternshipOrder.query.filter(
            InternshipOrder.screenshot_url.isnot(None)
        ).all()
        
        fixed_count = 0
        for order in internship_orders:
            old_url = order.screenshot_url
            if old_url:
                # Extract filename from old URL
                if 'internship_' in old_url:
                    filename = old_url.split('/')[-1]
                    # Remove 'internship_' prefix
                    if filename.startswith('internship_'):
                        new_filename = filename.replace('internship_', '')
                        new_url = f"/uploads/screenshots/{new_filename}"
                        
                        order.screenshot_url = new_url
                        print(f"✅ Fixed: {old_url} -> {new_url}")
                        fixed_count += 1
        
        db.session.commit()
        print(f"\n✅ Fixed {fixed_count} internship payment screenshot URLs")

if __name__ == "__main__":
    fix_internship_screenshot_urls()