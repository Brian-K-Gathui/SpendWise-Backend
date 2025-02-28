from server.routes.user_routes import UserResource, UserByIdResource

def register_routes(api):
    api.add_resource(UserResource, '/api/users')
    api.add_resource(UserByIdResource, '/api/users/<int:user_id>')
