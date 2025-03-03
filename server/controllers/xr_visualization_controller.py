from server.models import db, XRVisualization

def get_all_xr_visualizations():
    visualizations = [xr.serialize() for xr in XRVisualization.query.all()]
    return visualizations, 200

def get_xr_visualization_by_id(xr_id):
    xr = XRVisualization.query.get(xr_id)
    if not xr:
        return {"error": "XR Visualization not found"}, 404
    return xr.serialize(), 200

def create_xr_visualization(data):
    required_fields = ['user_id', 'visualization_type']
    for field in required_fields:
        if not data.get(field):
            return {"error": f"{field} is required"}, 400
    new_xr = XRVisualization(
        user_id=data.get('user_id'),
        visualization_type=data.get('visualization_type'),
        scene_data=data.get('scene_data'),
        interaction_metrics=data.get('interaction_metrics'),
        performance_stats=data.get('performance_stats')
    )
    db.session.add(new_xr)
    db.session.commit()
    return new_xr.serialize(), 201

def update_xr_visualization(xr_id, data):
    xr = XRVisualization.query.get(xr_id)
    if not xr:
        return {"error": "XR Visualization not found"}, 404
    for key, value in data.items():
        setattr(xr, key, value)
    db.session.commit()
    return xr.serialize(), 200

def delete_xr_visualization(xr_id):
    xr = XRVisualization.query.get(xr_id)
    if not xr:
        return {"error": "XR Visualization not found"}, 404
    db.session.delete(xr)
    db.session.commit()
    return {"message": "XR Visualization deleted successfully"}, 200
