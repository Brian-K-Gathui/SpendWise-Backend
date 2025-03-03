from server.models import db, FinancialBenchmark

def get_all_financial_benchmarks():
    benchmarks = [fb.serialize() for fb in FinancialBenchmark.query.all()]
    return benchmarks, 200

def get_financial_benchmark_by_id(benchmark_id):
    fb = FinancialBenchmark.query.get(benchmark_id)
    if not fb:
        return {"error": "Financial Benchmark not found"}, 404
    return fb.serialize(), 200

def create_financial_benchmark(data):
    required_fields = ['user_id']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_fb = FinancialBenchmark(
        user_id=data.get('user_id'),
        peer_group_params=data.get('peer_group_params'),
        comparison_metrics=data.get('comparison_metrics'),
        insights_generated=data.get('insights_generated'),
        recommendation_score=data.get('recommendation_score')
    )
    db.session.add(new_fb)
    db.session.commit()
    return new_fb.serialize(), 201

def update_financial_benchmark(benchmark_id, data):
    fb = FinancialBenchmark.query.get(benchmark_id)
    if not fb:
        return {"error": "Financial Benchmark not found"}, 404
    for key, value in data.items():
        setattr(fb, key, value)
    db.session.commit()
    return fb.serialize(), 200

def delete_financial_benchmark(benchmark_id):
    fb = FinancialBenchmark.query.get(benchmark_id)
    if not fb:
        return {"error": "Financial Benchmark not found"}, 404
    db.session.delete(fb)
    db.session.commit()
    return {"message": "Financial Benchmark deleted successfully"}, 200
