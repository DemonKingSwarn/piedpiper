import os
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import time
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/compressed_images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['TEMP_FILE_EXPIRATION'] = 3600  # 1 hour in seconds


"""
def compress_image(image):
   compressed_image = image.copy()
   compressed_image.save("compressed.jpg", optimize=True, quality=50)

   return compressed_image
"""

def compress_image(image):
    compressed_image = image.copy()

    # Get the pixel values of the image
    pixel_values = list(image.getdata())

    # Convert pixel values to integers
    flattened_pixels = [p for pixel in pixel_values for p in pixel]

    # Convert integers to bytes
    byte_values = bytes(flattened_pixels)

    # Create a new PIL image from the byte values
    compressed_image.frombytes(byte_values)

    return compressed_image

def delete_file_after_timeout(filepath, timeout):
    time.sleep(timeout)
    os.remove(filepath)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/compress', methods=['POST'])
def compress():
    if 'image' not in request.files:
        return redirect(url_for('upload_form'))

    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('upload_form'))

    if file and allowed_file(file.filename):
        # Save the uploaded file to a temporary location
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_filepath)

        # Open the uploaded image using PIL
        image = Image.open(temp_filepath)

        # Compress the image
        compressed_image = compress_image(image)

        # Generate a new filename for the compressed image
        compressed_filename = f"compressed_{os.path.splitext(file.filename)[0]}"

        # Save the compressed image
        compressed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{compressed_filename}.jpg')
        compressed_image.save(compressed_filepath)

        # Delete the temporary file
        os.remove(temp_filepath)
         # Start a thread to delete the file after the timeout
        timeout_thread = threading.Thread(target=delete_file_after_timeout, args=(compressed_filepath, app.config['TEMP_FILE_EXPIRATION']))
        timeout_thread.start()

        # Redirect to the display page with the compressed image
        return redirect(url_for('display', filename=compressed_filename))

@app.route('/display/<filename>')
def display(filename):
    compressed_image_path = url_for('static', filename=f"compressed_images/{filename}.jpg")
    return render_template('display.html', compressed_image=compressed_image_path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)


