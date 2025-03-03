from server.routes.user_routes import UserResource, UserByIdResource
from server.routes.transaction_routes import TransactionsResource, TransactionByIdResource
from server.routes.wallet__routes import WalletsResource, WalletByIdResource
from server.routes.categories_routes import CategoriesResource, CategoryByIdResource
from server.routes.wallet_collaborators_routes import WalletCollaboratorsResource, WalletCollaboratorByIdResource
from server.routes.budgets_routes import BudgetsResource, BudgetByIdResource
from server.routes.ai_advisor_routes import AIAdvisorProfilesResource, AIAdvisorProfileByIdResource
from server.routes.voice_transactions_routes import VoiceTransactionsResource, VoiceTransactionByIdResource
from server.routes.spending_patterns_routes import SpendingPatternsResource, SpendingPatternByIdResource
from server.routes.financial_benchmarks_routes import FinancialBenchmarksResource, FinancialBenchmarkByIdResource
from server.routes.xr_visualizations_routes import XRVisualizationsResource, XRVisualizationByIdResource
from server.routes.crypto_wallets_routes import CryptoWalletsResource, CryptoWalletByIdResource
from server.routes.financial_forecasts_routes import FinancialForecastsResource, FinancialForecastByIdResource
from server.routes.smart_categories_routes import SmartCategoriesResource, SmartCategoryByIdResource
from server.routes.wallet_invitations_routes import WalletInvitationsResource, WalletInvitationByIdResource
from server.routes.smart_budgets_routes import SmartBudgetsResource, SmartBudgetByIdResource
from server.routes.notifications_routes import NotificationsResource, NotificationByIdResource
from server.routes.receipt_scans_routes import ReceiptScansResource, ReceiptScanByIdResource

def register_routes(api):
    # User Routes
    api.add_resource(UserResource, '/api/users')
    api.add_resource(UserByIdResource, '/api/users/<int:user_id>')

    # Transaction Routes
    api.add_resource(TransactionsResource, '/api/transactions')
    api.add_resource(TransactionByIdResource, '/api/transactions/<int:transaction_id>')

    # Wallet Routes
    api.add_resource(WalletsResource, '/api/wallets')
    api.add_resource(WalletByIdResource, '/api/wallets/<int:wallet_id>')

    # Category Routes
    api.add_resource(CategoriesResource, '/api/categories')
    api.add_resource(CategoryByIdResource, '/api/categories/<int:category_id>')

    # Wallet Collaborator Routes
    api.add_resource(WalletCollaboratorsResource, '/api/wallets/<int:wallet_id>/collaborators')
    api.add_resource(WalletCollaboratorByIdResource, '/api/wallets/<int:wallet_id>/collaborators/<int:collaborator_id>')

    # Budget Routes
    api.add_resource(BudgetsResource, '/api/budgets')
    api.add_resource(BudgetByIdResource, '/api/budgets/<int:budget_id>')

    # AI Advisor Profiles Routes
    api.add_resource(AIAdvisorProfilesResource, '/api/ai-advisors')
    api.add_resource(AIAdvisorProfileByIdResource, '/api/ai-advisors/<int:profile_id>')

    # Voice Transactions Routes
    api.add_resource(VoiceTransactionsResource, '/api/voice-transactions')
    api.add_resource(VoiceTransactionByIdResource, '/api/voice-transactions/<int:vt_id>')

    # Spending Patterns Routes
    api.add_resource(SpendingPatternsResource, '/api/spending-patterns')
    api.add_resource(SpendingPatternByIdResource, '/api/spending-patterns/<int:pattern_id>')

    # Financial Benchmarks Routes
    api.add_resource(FinancialBenchmarksResource, '/api/financial-benchmarks')
    api.add_resource(FinancialBenchmarkByIdResource, '/api/financial-benchmarks/<int:benchmark_id>')

    # XR Visualizations Routes
    api.add_resource(XRVisualizationsResource, '/api/xr-visualizations')
    api.add_resource(XRVisualizationByIdResource, '/api/xr-visualizations/<int:xr_id>')

    # Crypto Wallets Routes
    api.add_resource(CryptoWalletsResource, '/api/crypto-wallets')
    api.add_resource(CryptoWalletByIdResource, '/api/crypto-wallets/<int:wallet_id>')

    # Financial Forecasts Routes
    api.add_resource(FinancialForecastsResource, '/api/financial-forecasts')
    api.add_resource(FinancialForecastByIdResource, '/api/financial-forecasts/<int:forecast_id>')

    # Smart Categories Routes
    api.add_resource(SmartCategoriesResource, '/api/smart-categories')
    api.add_resource(SmartCategoryByIdResource, '/api/smart-categories/<int:sc_id>')

    # Wallet Invitations Routes
    api.add_resource(WalletInvitationsResource, '/api/wallet-invitations')
    api.add_resource(WalletInvitationByIdResource, '/api/wallet-invitations/<int:invitation_id>')

    # Smart Budgets Routes
    api.add_resource(SmartBudgetsResource, '/api/smart-budgets')
    api.add_resource(SmartBudgetByIdResource, '/api/smart-budgets/<int:sb_id>')

    # Notifications Routes
    api.add_resource(NotificationsResource, '/api/notifications')
    api.add_resource(NotificationByIdResource, '/api/notifications/<int:notification_id>')

    # Receipt Scans Routes
    api.add_resource(ReceiptScansResource, '/api/receipt-scans')
    api.add_resource(ReceiptScanByIdResource, '/api/receipt-scans/<int:scan_id>')
