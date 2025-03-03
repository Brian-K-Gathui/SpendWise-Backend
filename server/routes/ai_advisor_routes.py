from flask import request
from flask_restful import Resource
from server.controllers.ai_advisor_controller import (
    get_all_ai_advisors,
    get_ai_advisor_by_id,
    create_ai_advisor,
    update_ai_advisor,
    delete_ai_advisor
)

class AIAdvisorProfilesResource(Resource):
    def get(self):
        profiles, status_code = get_all_ai_advisors()
        return profiles, status_code

    def post(self):
        data = request.get_json()
        profile, status_code = create_ai_advisor(data)
        return profile, status_code

class AIAdvisorProfileByIdResource(Resource):
    def get(self, profile_id):
        profile, status_code = get_ai_advisor_by_id(profile_id)
        return profile, status_code

    def patch(self, profile_id):
        data = request.get_json()
        profile, status_code = update_ai_advisor(profile_id, data)
        return profile, status_code

    def delete(self, profile_id):
        response, status_code = delete_ai_advisor(profile_id)
        return response, status_code
