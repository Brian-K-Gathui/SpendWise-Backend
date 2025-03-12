# 💵 SpendWise Backend - Personal & Collaborative Expense Tracker

<div align="center">
  <img src="https://i.imgur.com/YOUR_LOGO_HERE.png" alt="SpendWise Logo" width="200"/>

  [![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://spendwise-three.vercel.app/)
  [![Flask](https://img.shields.io/badge/Built%20with-Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
  [![Supabase](https://img.shields.io/badge/Auth-Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
</div>

## 🌐 Live Demo

[https://spendwise-three.vercel.app/](https://spendwise-three.vercel.app/)

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [API Endpoints](#api-endpoints)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Authentication & Authorization](#authentication--authorization)
- [Features](#features)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## 📝 Overview

SpendWise is a comprehensive expense tracking platform designed to help users manage personal and shared finances efficiently. The backend provides a robust RESTful API that powers the frontend application, handling everything from user authentication to transaction processing, budget management, and financial reporting.

## 🎯 Problem Statement

Managing personal and shared expenses efficiently is a common challenge. Many individuals struggle to track their spending, set budgets, and collaborate with others on shared financial responsibilities. Popular expense tracker applications often lack intuitive collaboration features, making it difficult for families, roommates, or business partners to manage joint expenses.

SpendWise aims to solve these problems by offering a comprehensive and user-friendly expense tracking platform. The application allows users to create and manage wallets, set budgets, categorize expenses and incomes, and collaborate with others through shared wallets. With a mobile-responsive UI and insightful dashboards, users gain full visibility into their financial habits, helping them make informed decisions.

## 🔌 API Endpoints

### Base URL
- Production: `https://spendwise-three.vercel.app/`

### User Management
- `GET /api/users/:id` - Get user details
- `POST /api/users` - Create or update user

### Wallet Management
- `GET /api/wallets` - Get all wallets for a user
- `GET /api/wallets/:id` - Get a specific wallet
- `POST /api/wallets` - Create a new wallet
- `PUT /api/wallets/:id` - Update a wallet
- `DELETE /api/wallets/:id` - Delete a wallet

### Transaction Management
- `GET /api/transactions` - Get all transactions (with optional filtering)
- `GET /api/transactions/:id` - Get a specific transaction
- `POST /api/transactions` - Create a new transaction
- `PUT /api/transactions/:id` - Update a transaction
- `DELETE /api/transactions/:id` - Delete a transaction

### Budget Management
- `GET /api/budgets` - Get all budgets (with optional filtering)
- `GET /api/budgets/:id` - Get a specific budget
- `POST /api/budgets` - Create a new budget
- `PUT /api/budgets/:id` - Update a budget
- `DELETE /api/budgets/:id` - Delete a budget

### Category Management
- `GET /api/categories` - Get all categories
- `GET /api/categories/:id` - Get a specific category
- `POST /api/categories` - Create a new category

### Notification Management
- `GET /api/notifications` - Get all notifications
- `GET /api/notifications/:id` - Get a specific notification
- `POST /api/notifications` - Create a new notification
- `PUT /api/notifications/:id` - Update a notification (e.g., mark as read)
- `DELETE /api/notifications/:id` - Delete a notification

### Recurring Transactions
- `GET /api/recurring-transactions` - Get all recurring transactions
- `GET /api/recurring-transactions/:id` - Get a specific recurring transaction
- `POST /api/recurring-transactions` - Create a new recurring transaction
- `PUT /api/recurring-transactions/:id` - Update a recurring transaction
- `DELETE /api/recurring-transactions/:id` - Delete a recurring transaction
- `POST /api/recurring-transactions/process` - Process due recurring transactions

### Reports
- `GET /api/reports` - Get all reports
- `GET /api/reports/:id` - Get a specific report
- `POST /api/reports` - Generate a new report
- `DELETE /api/reports/:id` - Delete a report

### Shared Wallets
- `GET /api/shared-wallets` - Get all shared wallets
- `GET /api/shared-wallets/:id` - Get a specific shared wallet
- `POST /api/shared-wallets` - Share a wallet with another user
- `PUT /api/shared-wallets/:id` - Update sharing permissions
- `DELETE /api/shared-wallets/:id` - Remove sharing access

## 🛠️ Tech Stack

### Backend Framework
- **Flask**: Lightweight WSGI web application framework
- **Flask-RESTful**: Extension for building REST APIs with Flask
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **Flask-Migrate**: Database migration handling

### Database
- **PostgreSQL**: Primary database for storing application data
- **Supabase**: Used for user data synchronization and authentication

### Authentication
- **JWT (JSON Web Tokens)**: For secure authentication
- **Clerk**: For user management and authentication (frontend integration)

### Deployment
- **Vercel**: Hosting platform for the backend API
- **Supabase**: Database hosting and authentication services

### Development Tools
- **Python 3.12**: Programming language
- **Pipenv**: Dependency management
- **dotenv**: Environment variable management

## 🏗️ Architecture

SpendWise follows a layered architecture pattern:

1. **API Layer** (`resources/`): Handles HTTP requests and responses
2. **Service Layer** (`services/`): Contains business logic
3. **Data Access Layer** (`models.py`): Manages database interactions
4. **Infrastructure** (Vercel, Supabase): Provides hosting and authentication

### Directory Structure

SpendWise-Backend/
├── .vercel/                  # Vercel deployment configuration
├── **pycache**/              # Python cache files
├── migrations/               # Database migration files
├── resources/                # API resource files
│   ├── budgetResource.py     # Budget API endpoints
│   ├── categoryResource.py   # Category API endpoints
│   ├── notificationResource.py # Notification API endpoints
│   ├── recurring_transaction_resource.py # Recurring transactions API
│   ├── report_resource.py    # Reports API endpoints
│   ├── shared_wallet_resource.py # Shared wallets API
│   ├── supabaseResource.py   # Supabase integration
│   ├── transactionResource.py # Transaction API endpoints
│   └── userResource.py       # User API endpoints
├── scripts/                  # Utility scripts
│   ├── seed_categories.py    # Script to seed default categories
│   ├── supabase_service.py   # Supabase service utilities
│   └── sync_users.py         # Script to sync users with Supabase
├── services/                 # Business logic services
│   ├── budget_service.py     # Budget-related business logic
│   ├── supabase_service.py   # Supabase integration service
│   └── transaction_service.py # Transaction-related business logic
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── app.py                    # Main application entry point
├── init.sql                  # Database initialization SQL
├── LICENSE.md                # License file
├── models.py                 # Database models
├── Pipfile                   # Pipenv dependencies
├── Pipfile.lock              # Pipenv lock file
├── README.md                 # Project documentation
├── seed.py                   # Database seeding script
└── vercel.json               # Vercel deployment


### configuration

## 📊 Database Schema

SpendWise uses a relational database with the following key models:

### User
- Stores user information and authentication details
- Links to wallets, transactions, budgets, and notifications

### Wallet
- Represents a financial account (personal, shared, savings)
- Contains balance, currency, and type information
- Can be shared with other users

### Transaction
- Records financial activities (income or expense)
- Linked to a wallet and optionally a category
- Includes amount, date, and description

### Budget
- Defines spending limits for specific categories
- Includes period (daily, weekly, monthly, yearly)
- Tracks start and end dates

### Category
- Classifies transactions (e.g., Food, Transport, Salary)
- Includes type (income or expense), icon, and color

### RecurringTransaction
- Manages scheduled transactions
- Supports various frequencies (daily, weekly, monthly, yearly)
- Automatically creates transactions when due

### Notification
- Alerts users about important events
- Includes budget alerts, shared wallet invites, etc.

### Report
- Stores generated financial reports
- Supports various report types (expense summary, income summary, etc.)

### SharedWallet
- Manages wallet sharing between users
- Defines access permissions (owner, editor, viewer)

## 🔐 Authentication & Authorization

SpendWise uses a token-based authentication system:

1. **JWT Authentication**: All API requests require a valid JWT token in the Authorization header
2. **Clerk Integration**: The frontend uses Clerk for user management, which provides JWTs
3. **Role-Based Access**: Users can only access their own data or shared resources they have permission for
4. **Supabase Sync**: User data is synchronized between the application database and Supabase

## ✨ Features

### User Management
- User registration and authentication
- Profile management
- Secure password handling

### Wallet Management
- Create multiple wallets for different purposes
- Track wallet balances in different currencies
- Share wallets with other users

### Transaction Tracking
- Record income and expenses
- Categorize transactions
- Filter and search transactions
- Recurring transactions support

### Budget Management
- Set budgets for specific categories
- Track budget progress
- Receive notifications for budget limits

### Reporting
- Generate financial reports
- Expense summaries by category
- Income analysis
- Budget performance tracking
- Cash flow analysis

### Collaboration
- Share wallets with family, friends, or colleagues
- Different permission levels (owner, editor, viewer)
- Real-time updates for shared resources

### Notifications
- Budget alerts
- Shared wallet invitations
- Security alerts

## 🚀 Installation & Setup

### Prerequisites
- Python 3.12 or higher
- PostgreSQL database
- Supabase account
- Pipenv (recommended for dependency management)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/spendwise-backend.git
   cd spendwise-backend
   ```

### **Install dependencies**
```bash
  pipenv install
```

- **Set up environment variables**
Create a `.env` file in the root directory with the required environment
variables (see [Environment Variables](#environment-variables) section).

```bash
# Flask configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
SECRET_KEY=your_secret_key

# Database configuration
DATABASE_URL=postgresql://username:password@localhost:5432/spendwise

# Supabase configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# JWT configuration
JWT_SECRET_KEY=your_jwt_secret_key

```


### Set up the database
# Create a PostgreSQL database
```bash
flask db init ->initialization
flask db migrate -> migrate
flask db upgrade - update remote schema
``

# Seed default categories
pipenv run python scripts/seed_categories.py


### **Run the application**
```bash
pipenv run flask run
```

- The API will be available at `http://localhost:5000`


## 📦 Deployment

SpendWise backend is deployed on Vercel:

1. **Set up Vercel CLI**

```bash
pnpm/npm/bun install -g vercel
```
### Deploy to Vercel

```bash
vercel
```

3. **Set environment variables on Vercel**
Configure all required environment variables in the Vercel dashboard.
4. **Database setup**

1. Create a PostgreSQL database on Supabase
2. Run migrations and seed scripts against the production database





## 📚 API Documentation

Detailed API documentation is available at:

- [Postman Collection](https://www.postman.com/your-collection-link)
