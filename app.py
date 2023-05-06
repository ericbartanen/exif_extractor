from flask import Flask, request
from PIL import Image, TiffImagePlugin
from PIL.ExifTags import TAGS, GPSTAGS, IFD
import json

app = Flask(__name__)

@app.route('/hello/', methods=['GET', 'POST'])
def welcome():
    return "Hello World!"

@app.route('/test/', methods=['GET', 'POST'])
def test():
    if request.method == "POST":
        img = request.files['image']
        return getGPS(img)

def getGPS(image):
    im = Image.open(image)     # Open image
    exif = im.getexif()                 # Extract exif data
    gps_ifd = exif.get_ifd(IFD.GPSInfo) # Convert exif GPS codes to GPS titles
    coordinates = []

    ########################################################
    # Code citation:
    # Cast function converts objects that cannot be turned into JSON into objects that can.
    # This code was copied from stackoverflow:
    # https://github.com/python-pillow/Pillow/issues/6199
    ############################################################

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