from flask import Flask, request
from PIL import Image, TiffImagePlugin
from PIL.ExifTags import GPSTAGS, IFD, TAGS
import json

ALLOWED_EXTENSIONS = {'jpg', 'jpeg' ,'png'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 * 1000  # 10MB limit

@app.route('/latlng/', methods=['POST'])
def latlng():
    if request.method == "POST":
        
        #check for image in request
        if 'image' not in request.files:
            return "No image found"

        img = request.files['image']

        # check file type
        if img.mimetype not in ['image/jpeg', 'image/png']:
            return "Unsupported image format."
        print(img.mimetype)
        try:
            img.stream.seek(0)
            return getGPS(img)
        except Exception as e:
            return str(e)

def getGPS(image):
    im = Image.open(image)              # Open image
    exif = im.getexif()                 # Extract exif data
    gps_ifd = exif.get_ifd(IFD.GPSInfo) # Convert exif GPS codes to GPS titles

   # gps_ifd returns a dictionary, if it's empty than no lat/lng data is present
    if not gps_ifd:
        return "No Latitude or Longitude found."

    coordinates = []

    '''
    Code citation: https://github.com/python-pillow/Pillow/issues/6199
    Some GPS codes from exif.get_ifg() cannot be parsed with normal methods so they need to be converted into readable objects.
    '''
    def cast(v):
        if isinstance(v, TiffImagePlugin.IFDRational):
            return float(v)
        elif isinstance(v, tuple):
            return tuple(cast(t) for t in v)
        elif isinstance(v, bytes):
            return v.decode(errors="replace")
        elif isinstance(v, dict):
            for key, value in v.items():
                v[key] = cast(value)
            return v
        else: return v

    # Create array with relevant Lat and Long data
    for key, value in gps_ifd.items():
        if GPSTAGS.get(key) in ['GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude']:
            value = cast(value)
            coordinates.append({str(GPSTAGS.get(key)): value})

    json_coordinates = json.dumps(coordinates)
    return json_coordinates

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3003)