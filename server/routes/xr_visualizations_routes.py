from flask import request
from flask_restful import Resource
from server.controllers.xr_visualization_controller import (
    get_all_xr_visualizations,
    get_xr_visualization_by_id,
    create_xr_visualization,
    update_xr_visualization,
    delete_xr_visualization
)

class XRVisualizationsResource(Resource):
    def get(self):
        visualizations, status_code = get_all_xr_visualizations()
        return visualizations, status_code

    def post(self):
        data = request.get_json()
        xr, status_code = create_xr_visualization(data)
        return xr, status_code

class XRVisualizationByIdResource(Resource):
    def get(self, xr_id):
        xr, status_code = get_xr_visualization_by_id(xr_id)
        return xr, status_code

    def patch(self, xr_id):
        data = request.get_json()
        xr, status_code = update_xr_visualization(xr_id, data)
        return xr, status_code

    def delete(self, xr_id):
        response, status_code = delete_xr_visualization(xr_id)
        return response, status_code
