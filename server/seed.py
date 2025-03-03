from faker import Faker
from random import choice, uniform, randint
from datetime import datetime, timedelta
from server.config import app, db
from server.models import (
    User, Wallet, Transaction, Category, WalletCollaborator, Budget,
    AIAdvisorProfile, VoiceTransaction, SpendingPattern, FinancialBenchmark,
    XRVisualization, CryptoWallet, FinancialForecast, SmartCategory,
    WalletInvitation, SmartBudget, Notification, ReceiptScan
)

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
    total_users = len(admin_users) + len(regular_users)
    print(f"✅ Seeded {total_users} users!\n")
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
    return collaborators

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
    return budgets

def seed_ai_advisor_profiles(users):
    print("🤖 Seeding AI Advisor Profiles...")
    profiles = []
    for user in users:
        profile = AIAdvisorProfile(
            user_id=user.id,
            risk_tolerance=round(uniform(0, 1), 2),
            financial_goals={"goal": fake.sentence()},
            investment_preferences={"preference": fake.word()},
            learning_parameters={"param": randint(1, 10)}
        )
        db.session.add(profile)
        profiles.append(profile)
    db.session.commit()
    print(f"✅ Seeded {len(profiles)} AI Advisor Profiles!\n")
    return profiles

def seed_voice_transactions(users):
    print("🎤 Seeding Voice Transactions...")
    voice_transactions = []
    for _ in range(20):
        vt = VoiceTransaction(
            user_id=choice(users).id,
            audio_url=fake.url(),
            transcription=fake.sentence(),
            intent_analysis={"intent": fake.word()},
            extracted_data={"data": fake.sentence()},
            confidence_score=round(uniform(0.5, 1), 2),
            status=choice(["processing", "completed", "failed"])
        )
        if vt.status == "completed":
            vt.processed_at = datetime.utcnow()
        db.session.add(vt)
        voice_transactions.append(vt)
    db.session.commit()
    print(f"✅ Seeded {len(voice_transactions)} Voice Transactions!\n")
    return voice_transactions

def seed_spending_patterns(users):
    print("📊 Seeding Spending Patterns...")
    patterns = []
    for _ in range(15):
        sp = SpendingPattern(
            user_id=choice(users).id,
            pattern_type=choice(["habit", "anomaly", "opportunity"]),
            pattern_data={"detail": fake.sentence()},
            significance_score=round(uniform(0, 10), 2),
            recognition_params={"param": fake.word()},
            actions_suggested={"action": fake.word()}
        )
        db.session.add(sp)
        patterns.append(sp)
    db.session.commit()
    print(f"✅ Seeded {len(patterns)} Spending Patterns!\n")
    return patterns

def seed_financial_benchmarks(users):
    print("📈 Seeding Financial Benchmarks...")
    benchmarks = []
    for _ in range(10):
        fb = FinancialBenchmark(
            user_id=choice(users).id,
            peer_group_params={"group": fake.word()},
            comparison_metrics={"metric": round(uniform(0, 100), 2)},
            insights_generated={"insight": fake.sentence()},
            recommendation_score=round(uniform(0, 5), 2)
        )
        db.session.add(fb)
        benchmarks.append(fb)
    db.session.commit()
    print(f"✅ Seeded {len(benchmarks)} Financial Benchmarks!\n")
    return benchmarks

def seed_xr_visualizations(users):
    print("🌐 Seeding XR Visualizations...")
    visualizations = []
    for _ in range(8):
        xr = XRVisualization(
            user_id=choice(users).id,
            visualization_type=choice(["ar_overlay", "vr_space", "mixed_reality"]),
            scene_data={"scene": fake.word()},
            interaction_metrics={"clicks": randint(1, 100)},
            performance_stats={"fps": round(uniform(24, 60), 2)}
        )
        db.session.add(xr)
        visualizations.append(xr)
    db.session.commit()
    print(f"✅ Seeded {len(visualizations)} XR Visualizations!\n")
    return visualizations

def seed_crypto_wallets(users):
    print("💎 Seeding Crypto Wallets...")
    crypto_wallets = []
    for _ in range(10):
        cw = CryptoWallet(
            user_id=choice(users).id,
            wallet_address=fake.sha256(),
            blockchain_type=choice(["Bitcoin", "Ethereum", "Ripple"]),
            balance_snapshot={"balance": round(uniform(0, 10), 2)},
            transaction_history={"transactions": [fake.word() for _ in range(3)]},
            risk_assessment={"risk": round(uniform(0, 1), 2)}
        )
        db.session.add(cw)
        crypto_wallets.append(cw)
    db.session.commit()
    print(f"✅ Seeded {len(crypto_wallets)} Crypto Wallets!\n")
    return crypto_wallets

def seed_financial_forecasts(users, wallets):
    print("🔮 Seeding Financial Forecasts...")
    forecasts = []
    for _ in range(10):
        ff = FinancialForecast(
            user_id=choice(users).id,
            wallet_id=choice(wallets).id,
            forecast_type=choice(["spending", "income", "savings", "investment"]),
            time_range=choice(["weekly", "monthly", "quarterly", "yearly"]),
            prediction_data={"prediction": round(uniform(100, 1000), 2)},
            confidence_interval={"min": 0.8, "max": 1.0},
            model_version="1.0",
            accuracy_metrics={"accuracy": round(uniform(0, 100), 2)}
        )
        ff.valid_until = datetime.utcnow() + timedelta(days=randint(30, 365))
        db.session.add(ff)
        forecasts.append(ff)
    db.session.commit()
    print(f"✅ Seeded {len(forecasts)} Financial Forecasts!\n")
    return forecasts

def seed_smart_categories(categories):
    print("🤖 Seeding Smart Categories...")
    smart_categories = []
    for cat in categories:
        if choice([True, False]):
            sc = SmartCategory(
                name=f"Smart {cat.name}",
                parent_category_id=cat.id,
                rules_set={"rule": fake.word()},
                learning_threshold=round(uniform(0.1, 1), 2),
                confidence_minimum=round(uniform(0.5, 1), 2)
            )
            db.session.add(sc)
            smart_categories.append(sc)
    db.session.commit()
    print(f"✅ Seeded {len(smart_categories)} Smart Categories!\n")
    return smart_categories

def seed_wallet_invitations(wallets, users):
    print("✉️ Seeding Wallet Invitations...")
    invitations = []
    for _ in range(8):
        inv = WalletInvitation(
            wallet_id=choice(wallets).id,
            invited_by=choice(users).id,
            invited_email=fake.email(),
            permission_level=choice(["editor", "viewer"]),
            status=choice(["pending", "accepted", "rejected"])
        )
        inv.expires_at = datetime.utcnow() + timedelta(days=randint(7, 30))
        db.session.add(inv)
        invitations.append(inv)
    db.session.commit()
    print(f"✅ Seeded {len(invitations)} Wallet Invitations!\n")
    return invitations

def seed_smart_budgets(budgets):
    print("⚙️ Seeding Smart Budgets...")
    smart_budgets = []
    for budget in budgets:
        if choice([True, False]):
            sb = SmartBudget(
                budget_id=budget.id,
                ai_parameters={"param": fake.word()},
                market_conditions={"condition": fake.word()},
                adjustment_history={"adjustments": [randint(0, 5)]},
                performance_metrics={"performance": round(uniform(0, 100), 2)},
                suggestion_log={"suggestion": fake.sentence()}
            )
            db.session.add(sb)
            smart_budgets.append(sb)
    db.session.commit()
    print(f"✅ Seeded {len(smart_budgets)} Smart Budgets!\n")
    return smart_budgets

def seed_notifications(users):
    print("🔔 Seeding Notifications...")
    notifications = []
    for _ in range(20):
        n = Notification(
            user_id=choice(users).id,
            type=choice(["budget_alert", "shared_wallet_invite", "security_alert"]),
            title=fake.sentence(nb_words=5),
            message=fake.text(max_nb_chars=100),
            is_read=choice([True, False])
        )
        db.session.add(n)
        notifications.append(n)
    db.session.commit()
    print(f"✅ Seeded {len(notifications)} Notifications!\n")
    return notifications

def seed_receipt_scans(users):
    print("🧾 Seeding Receipt Scans...")
    receipt_scans = []
    for _ in range(10):
        rs = ReceiptScan(
            user_id=choice(users).id,
            image_url=fake.image_url(),
            ocr_text=fake.text(max_nb_chars=100),
            confidence_score=round(uniform(0.5, 1), 2),
            merchant_name=fake.company(),
            purchase_date=datetime.utcnow() - timedelta(days=randint(1, 365)),
            items_detected={"items": [fake.word() for _ in range(3)]},
            total_amount=round(uniform(10, 500), 2),
            status=choice(["processing", "completed", "failed"])
        )
        if rs.status == "completed":
            rs.processed_at = datetime.utcnow()
        db.session.add(rs)
        receipt_scans.append(rs)
    db.session.commit()
    print(f"✅ Seeded {len(receipt_scans)} Receipt Scans!\n")
    return receipt_scans

if __name__ == '__main__':
    with app.app_context():
        print("\n🚀 Starting the database seeding process...\n")

        # Clear existing data from all tables
        db.session.query(WalletInvitation).delete()
        db.session.query(SmartBudget).delete()
        db.session.query(SmartCategory).delete()
        db.session.query(FinancialForecast).delete()
        db.session.query(CryptoWallet).delete()
        db.session.query(XRVisualization).delete()
        db.session.query(FinancialBenchmark).delete()
        db.session.query(SpendingPattern).delete()
        db.session.query(VoiceTransaction).delete()
        db.session.query(AIAdvisorProfile).delete()
        db.session.query(Notification).delete()
        db.session.query(ReceiptScan).delete()
        db.session.query(Budget).delete()
        db.session.query(WalletCollaborator).delete()
        db.session.query(Transaction).delete()
        db.session.query(Category).delete()
        db.session.query(Wallet).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("🗑️  Cleared old database records!\n")

        # Seed base data
        users = seed_users()
        wallets = seed_wallets(users)
        categories = seed_categories(users)
        seed_transactions(wallets, users, categories)
        seed_wallet_collaborators(wallets, users)
        budgets = seed_budgets(wallets, users, categories)

        # Seed new features
        seed_ai_advisor_profiles(users)
        seed_voice_transactions(users)
        seed_spending_patterns(users)
        seed_financial_benchmarks(users)
        seed_xr_visualizations(users)
        seed_crypto_wallets(users)
        seed_financial_forecasts(users, wallets)
        seed_smart_categories(categories)
        seed_wallet_invitations(wallets, users)
        seed_smart_budgets(budgets)
        seed_notifications(users)
        seed_receipt_scans(users)

        print("🎉 Database seeding process completed successfully! 🚀\n")
