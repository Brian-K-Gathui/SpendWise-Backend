from server.models import db, FinancialForecast
from datetime import datetime

def get_all_financial_forecasts():
    forecasts = [ff.serialize() for ff in FinancialForecast.query.all()]
    return forecasts, 200

def get_financial_forecast_by_id(forecast_id):
    ff = FinancialForecast.query.get(forecast_id)
    if not ff:
        return {"error": "Financial Forecast not found"}, 404
    return ff.serialize(), 200

def create_financial_forecast(data):
    required_fields = ['user_id', 'wallet_id', 'forecast_type', 'time_range']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_ff = FinancialForecast(
        user_id=data.get('user_id'),
        wallet_id=data.get('wallet_id'),
        forecast_type=data.get('forecast_type'),
        time_range=data.get('time_range'),
        prediction_data=data.get('prediction_data'),
        confidence_interval=data.get('confidence_interval'),
        model_version=data.get('model_version'),
        accuracy_metrics=data.get('accuracy_metrics')
    )
    if data.get('valid_until'):
        try:
            new_ff.valid_until = datetime.fromisoformat(data.get('valid_until'))
        except Exception:
            return {"error": "Invalid valid_until format. Please use ISO format."}, 400
    db.session.add(new_ff)
    db.session.commit()
    return new_ff.serialize(), 201

def update_financial_forecast(forecast_id, data):
    ff = FinancialForecast.query.get(forecast_id)
    if not ff:
        return {"error": "Financial Forecast not found"}, 404
    for key, value in data.items():
        if key == 'valid_until' and value:
            try:
                value = datetime.fromisoformat(value)
            except Exception:
                return {"error": "Invalid valid_until format. Please use ISO format."}, 400
        setattr(ff, key, value)
    db.session.commit()
    return ff.serialize(), 200

def delete_financial_forecast(forecast_id):
    ff = FinancialForecast.query.get(forecast_id)
    if not ff:
        return {"error": "Financial Forecast not found"}, 404
    db.session.delete(ff)
    db.session.commit()
    return {"message": "Financial Forecast deleted successfully"}, 200
