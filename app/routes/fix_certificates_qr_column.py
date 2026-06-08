# fix_certificates_qr_column.py
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Alter column type to TEXT
    try:
        db.session.execute(text("ALTER TABLE certificates ALTER COLUMN qr_code_url TYPE TEXT"))
        db.session.commit()
        print("✅ Changed qr_code_url column to TEXT")
    except Exception as e:
        print(f"Error altering column: {e}")
    
    # Also increase other potential problem columns
    try:
        db.session.execute(text("ALTER TABLE certificates ALTER COLUMN verification_token TYPE VARCHAR(300)"))
        db.session.commit()
        print("✅ Increased verification_token column size")
    except Exception as e:
        print(f"Error altering verification_token: {e}")
    
    try:
        db.session.execute(text("ALTER TABLE certificates ALTER COLUMN certificate_hash TYPE VARCHAR(500)"))
        db.session.commit()
        print("✅ Increased certificate_hash column size")
    except Exception as e:
        print(f"Error altering certificate_hash: {e}")
    
    print("\n✅ Database fix completed!")