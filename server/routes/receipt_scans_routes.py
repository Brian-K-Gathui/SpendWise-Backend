from flask import request
from flask_restful import Resource
from server.controllers.receipt_scan_controller import (
    get_all_receipt_scans,
    get_receipt_scan_by_id,
    create_receipt_scan,
    update_receipt_scan,
    delete_receipt_scan
)

class ReceiptScansResource(Resource):
    def get(self):
        scans, status_code = get_all_receipt_scans()
        return scans, status_code

    def post(self):
        data = request.get_json()
        scan, status_code = create_receipt_scan(data)
        return scan, status_code

class ReceiptScanByIdResource(Resource):
    def get(self, scan_id):
        scan, status_code = get_receipt_scan_by_id(scan_id)
        return scan, status_code

    def patch(self, scan_id):
        data = request.get_json()
        scan, status_code = update_receipt_scan(scan_id, data)
        return scan, status_code

    def delete(self, scan_id):
        response, status_code = delete_receipt_scan(scan_id)
        return response, status_code
