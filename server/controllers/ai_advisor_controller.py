from server.models import db, AIAdvisorProfile

def get_all_ai_advisors():
    profiles = [profile.serialize() for profile in AIAdvisorProfile.query.all()]
    return profiles, 200

def get_ai_advisor_by_id(profile_id):
    profile = AIAdvisorProfile.query.get(profile_id)
    if not profile:
        return {"error": "AI Advisor Profile not found"}, 404
    return profile.serialize(), 200

def create_ai_advisor(data):
    required_fields = ['user_id', 'risk_tolerance']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_profile = AIAdvisorProfile(
        user_id=data.get('user_id'),
        risk_tolerance=data.get('risk_tolerance'),
        financial_goals=data.get('financial_goals'),
        investment_preferences=data.get('investment_preferences'),
        learning_parameters=data.get('learning_parameters')
    )
    db.session.add(new_profile)
    db.session.commit()
    return new_profile.serialize(), 201

def update_ai_advisor(profile_id, data):
    profile = AIAdvisorProfile.query.get(profile_id)
    if not profile:
        return {"error": "AI Advisor Profile not found"}, 404
    for key, value in data.items():
        setattr(profile, key, value)
    db.session.commit()
    return profile.serialize(), 200

def delete_ai_advisor(profile_id):
    profile = AIAdvisorProfile.query.get(profile_id)
    if not profile:
        return {"error": "AI Advisor Profile not found"}, 404
    db.session.delete(profile)
    db.session.commit()
    return {"message": "AI Advisor Profile deleted successfully"}, 200
