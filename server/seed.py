from faker import Faker
from server.config import app, db
from server.models import User

fake = Faker()

if __name__ == '__main__':
    with app.app_context():
        print("\n🚀 Starting user seed process...\n")

        # Clearing old user data
        print("🗑️  Clearing old users...")
        db.session.query(User).delete()
        db.session.commit()
        print("✅ Old users cleared!\n")

        # Seeding Admin Users
        print("👨‍💼 Seeding admin users...")
        admin_users = [
            User(
                username=f"admin{i}",
                email=f"admin{i}@example.com",
                full_name=fake.name(),
                phone_number=fake.phone_number(),
                is_verified=True,
                mfa_enabled=False,
                role="admin"
            )
            for i in range(1, 6)  # Creating 5 admin users
        ]
        for admin in admin_users:
            admin.set_password("adminpass")
        db.session.add_all(admin_users)
        db.session.commit()
        print(f"✅ Seeded {len(admin_users)} admin users!\n")

        # Seeding Regular Users
        print("🙋 Seeding regular users...")
        regular_users = [
            User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                full_name=fake.name(),
                phone_number=fake.phone_number(),
                is_verified=True,
                mfa_enabled=False,
                role="user"
            )
            for i in range(1, 21)  # Creating 20 regular users
        ]
        for user in regular_users:
            user.set_password("userpass")
        db.session.add_all(regular_users)
        db.session.commit()
        print(f"✅ Seeded {len(regular_users)} regular users!\n")

        print("🎉 User seeding process completed successfully! 🚀\n")
