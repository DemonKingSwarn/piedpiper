import os
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/compressed_images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


"""
def compress_image(image):
   compressed_image = image.copy()
   compressed_image.save("compressed.jpg", optimize=True, quality=50)

   return compressed_image
"""

def compress_image(image):
    compressed_image = image.copy()

    pixel_values = list(image.getdata())

    flattened_pixels = [p for pixel in pixel_values for p in pixel]

    byte_values = bytes(flattened_pixels)

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
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_filepath)

        image = Image.open(temp_filepath)

        compressed_image = compress_image(image)

        compressed_filename = f"compressed_{os.path.splitext(file.filename)[0]}"

        compressed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{compressed_filename}.jpg')
        compressed_image.save(compressed_filepath)

        os.remove(temp_filepath)

        return redirect(url_for('display', filename=compressed_filename))

@app.route('/display/<filename>')
def display(filename):
    compressed_image_path = url_for('static', filename=f"compressed_images/{filename}.jpg")
    return render_template('display.html', compressed_image=compressed_image_path)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)


