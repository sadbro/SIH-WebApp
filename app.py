from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from services import nn
from cv2 import imwrite

app = Flask(__name__)
content = macrofilepath = microfilepath = contourfilepath = ''

app.config["UPLOAD_FOLDER"] = "static/"

@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/display', methods=['GET', 'POST'])
def display_file():
    global content, macrofilepath, microfilepath, contourfilepath
    if request.method == 'POST':
        macrof = request.files['macroscopic']
        microf = request.files['microscopic']
        macrofilename = secure_filename(macrof.filename)
        microfilename = secure_filename(microf.filename)

        macrof.save(app.config['UPLOAD_FOLDER'] + 'macros/' + macrofilename)
        microf.save(app.config['UPLOAD_FOLDER'] + 'micros/' + microfilename)
        macrofilepath = app.config['UPLOAD_FOLDER'] + 'macros/' + macrofilename
        microfilepath = app.config['UPLOAD_FOLDER'] + 'micros/' + microfilename
        contourfilepath = app.config['UPLOAD_FOLDER'] + 'contours/' + macrofilename

        lithotype = nn.get_lithotype(macrofilepath, microfilepath) if nn.get_lithotype(macrofilepath, microfilepath) != -1 else 'N/A'
        clusters, grain_size = nn.get_grain_size(macrofilepath, 1600)
        fractures, contour_image, _ = nn.get_approx_fractures(macrofilepath)
        roundness = nn.get_roundness(clusters)
        sorting = nn.get_sorting(clusters)
        imwrite(contourfilepath, contour_image)
        content = {
            'Lithotype of Sample': lithotype,
            'Average Grain Size': "{}".format(round(grain_size, 4)),
            'Number of Fractures': fractures,
            'Roundness of Sample': "{} %".format(round(roundness * 100, 4)),
            'Sorting of Sample': sorting
        }

    return render_template('content.html',
                           content=content,
                           src_micro=microfilepath,
                           src_macro=macrofilepath,
                           src_contour=contourfilepath)

if __name__ == '__main__':
    app.run(debug=True)
