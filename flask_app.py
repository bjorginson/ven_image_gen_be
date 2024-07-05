from flask import Flask, request, jsonify, send_file
from tasks import process_request
from celery_config import app
import os
import logging
from flask_cors import CORS
import base64

flask_app = Flask(__name__)
CORS(flask_app)


@flask_app.route('/enqueue', methods=['POST'])
def enqueue():
    data = request.json
    print("data list", data['data']['prompt'])
    print("data list", data['data']['userId'])
    if not data or 'data' not in data:
        return jsonify({'error': 'Invalid request, please provide data'}), 400

    task = process_request.delay(data['data'])
    return jsonify({'task_id': task.id}), 202


@flask_app.route('/result/<task_id>', methods=['GET'])
def task_result(task_id):
    task = app.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        if task.result:
            image_path = task.result
            logging.debug(f"Task result path: {image_path}")
            if os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(
                        image_file.read()).decode('utf-8')
                    return jsonify({
                        'state': task.state,
                        'image': encoded_string
                    })
                # logging.debug(f"File exists: {image_path}")
                # return send_file(
                #     image_path,
                #     mimetype='image/png',
                # )
            else:
                logging.error(f"File not found: {image_path}")
                return jsonify({'error': 'File not found'}), 404
        else:
            response = {
                'state': task.state,
                'status': 'Task completed but no result found'
            }
    else:
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
