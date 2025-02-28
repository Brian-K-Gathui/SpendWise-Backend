from faker import Faker
from server.config import app, db
from server.models import User, Wallet, Transaction, Category, WalletCollaborator, Budget
from random import choice, uniform, randint
from datetime import datetime, timedelta

fake = Faker()

def seed_users():
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
        for i in range(1, 6)
    ]
    for admin in admin_users:
        admin.set_password("adminpass")

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
        for i in range(1, 21)
    ]
    for user in regular_users:
        user.set_password("userpass")

    db.session.add_all(admin_users + regular_users)
    db.session.commit()
    print(f"✅ Seeded {len(admin_users) + len(regular_users)} users!\n")
    return admin_users + regular_users

def seed_wallets(users):
    print("👛 Seeding wallets...")
    wallets = [
        Wallet(
            name=fake.word().capitalize() + " Wallet",
            description=fake.sentence(),
            currency=choice(["USD", "KES", "EUR"]),
            balance=round(uniform(1000, 10000), 2),
            type=choice(["personal", "shared"]),
            owner_id=choice(users).id
        )
        for _ in range(15)
    ]

    db.session.add_all(wallets)
    db.session.commit()
    print(f"✅ Seeded {len(wallets)} wallets!\n")
    return wallets

def seed_categories(users):
    print("📂 Seeding categories...")
    categories = [
        Category(
            name=name,
            type=choice(["expense", "income"]),
            icon="📌",
            color=fake.color_name(),
            is_default=choice([True, False]),
            created_by=choice(users).id if not choice([True, False]) else None
        )
        for name in ["Food", "Rent", "Salary", "Entertainment", "Savings"]
    ]

    db.session.add_all(categories)
    db.session.commit()
    print(f"✅ Seeded {len(categories)} categories!\n")
    return categories

def seed_transactions(wallets, users, categories):
    print("💰 Seeding transactions...")
    transactions = [
        Transaction(
            wallet_id=choice(wallets).id,
            category_id=choice(categories).id,
            amount=round(uniform(50, 5000), 2),
            type=choice(["expense", "income"]),
            description=fake.sentence(),
            date=fake.date_between(start_date="-1y", end_date="today"),
            is_recurring=choice([True, False]),
            recurring_interval=choice(["daily", "weekly", "monthly"]) if choice([True, False]) else None,
            created_by=choice(users).id
        )
        for _ in range(50)
    ]

    db.session.add_all(transactions)
    db.session.commit()
    print(f"✅ Seeded {len(transactions)} transactions!\n")

def seed_wallet_collaborators(wallets, users):
    print("👥 Seeding wallet collaborators...")
    collaborators = [
        WalletCollaborator(
            wallet_id=choice(wallets).id,
            user_id=choice(users).id,
            permission_level=choice(["owner", "editor", "viewer"])
        )
        for _ in range(10)
    ]

    db.session.add_all(collaborators)
    db.session.commit()
    print(f"✅ Seeded {len(collaborators)} wallet collaborators!\n")

def seed_budgets(wallets, users, categories):
    print("🎯 Seeding budgets...")
    budgets = [
        Budget(
            user_id=choice(users).id,
            category_id=choice(categories).id,
            wallet_id=choice(wallets).id,
            amount=round(uniform(500, 5000), 2),
            period=choice(["monthly", "quarterly", "yearly"]),
            start_date=datetime.utcnow() - timedelta(days=randint(10, 300)),
            end_date=datetime.utcnow() + timedelta(days=randint(30, 365))
        )
        for _ in range(10)
    ]

    db.session.add_all(budgets)
    db.session.commit()
    print(f"✅ Seeded {len(budgets)} budgets!\n")

if __name__ == '__main__':
    with app.app_context():
        print("\n🚀 Starting the database seeding process...\n")

        # Clear existing data
        db.session.query(WalletCollaborator).delete()
        db.session.query(Transaction).delete()
        db.session.query(Budget).delete()
        db.session.query(Category).delete()
        db.session.query(Wallet).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("🗑️  Cleared old database records!\n")

        # Seed data
        users = seed_users()
        wallets = seed_wallets(users)
        categories = seed_categories(users)
        seed_transactions(wallets, users, categories)
        seed_wallet_collaborators(wallets, users)
        seed_budgets(wallets, users, categories)

        print("🎉 Database seeding process completed successfully! 🚀\n")
