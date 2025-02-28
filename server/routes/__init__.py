from server.routes.user_routes import UserResource, UserByIdResource
from server.routes.transaction_routes import TransactionsResource, TransactionByIdResource
from server.routes.wallet__routes import WalletsResource, WalletByIdResource
from server.routes.categories_routes import CategoriesResource, CategoryByIdResource
from server.routes.wallet_collaborators_routes import WalletCollaboratorsResource, WalletCollaboratorByIdResource
from server.routes.budgets_routes import BudgetsResource, BudgetByIdResource

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
