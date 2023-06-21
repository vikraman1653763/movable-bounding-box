from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64

app = Flask(__name__)

# Global variables to store image data and bounding boxes
image_data = None
bounding_boxes = []

@app.route('/')
def index():
    return render_template('moveobj1.html')

@app.route('/process', methods=['POST'])
def process():
    global image_data, bounding_boxes

    image_file = request.files['image']
    txt_file = request.files['txt']

    txt_content = txt_file.read().decode('utf-8')

    image_array = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    image_height, image_width, _ = image.shape

    bounding_boxes = []
    for line in txt_content.splitlines():
        values = line.strip().split(' ')
        obj_id, x_norm, y_norm, width_norm, height_norm = values

        obj_id = int(obj_id)
        x_norm, y_norm, width_norm, height_norm = float(x_norm), float(y_norm), float(width_norm), float(height_norm)

        x = int((x_norm - width_norm / 2) * image_width)
        y = int((y_norm - height_norm / 2) * image_height)
        width = int(width_norm * image_width)
        height = int(height_norm * image_height)

    

        bbox = {'id': obj_id, 'x': x, 'y': y, 'width': width, 'height': height}
        bounding_boxes.append(bbox)

    _, processed_image = cv2.imencode('.jpg', image)
    image_data = base64.b64encode(processed_image).decode('utf-8')

    return render_template('moveobj2.html', image_data=image_data, bounding_boxes=bounding_boxes)

@app.route('/save', methods=['POST'])
def save():
    global image_data, bounding_boxes

    data = request.get_json()
    # Save the image data and bounding box data to your storage or database
    # ...

    # Update the bounding box positions on the image
    image_array = base64.b64decode(data['image_data'])
    image = cv2.imdecode(np.frombuffer(image_array, dtype=np.uint8), cv2.IMREAD_COLOR)
    
    for box in data['bounding_boxes']:
        x = box['x']
        y = box['y']
        width = box['width']
        height = box['height']
        cv2.rectangle(image, (x, y), (x + width, y + height), (0, 0, 255), 2)

    _, processed_image = cv2.imencode('.jpg', image)
    image_data = base64.b64encode(processed_image).decode('utf-8')

    return jsonify({'message': 'Image and bounding box data saved successfully.'})

@app.route('/otherpage')
def otherpage():
    global image_data, bounding_boxes

    # Load the saved image data and bounding box data from your storage or database
    # ...

    # Remove the red box from bounding_boxes
    bounding_boxes = []

    return render_template('moveobj3.html', image_data=image_data, bounding_boxes=bounding_boxes)

if __name__ == '__main__':
    app.run(debug=True)
