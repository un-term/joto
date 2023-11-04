from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os,sys,inspect
import joto

# Test Setup
# ------------------------------------------------------------------------------
if not os.path.exists("test_workspace"):
    os.makedirs("test_workspace")        
# load config and setup objects
if os.path.isfile("test_config.json"):
    json_config = joto.JsonConfig("test_config.json")
else:
    print("Missing config file")
    exit() 

sqlite_db = joto.JotoSQLiteDB(json_config.sqlite_db_path)
images_manage = joto.ImagesManage(json_config.image_size, json_config.original_image_dirpath, json_config.compressed_image_dirpath)
html = joto.HTML("./templates/output.html", json_config.html_output_path, json_config.compressed_image_dirpath)
joto_obj = joto.Joto(sqlite_db, images_manage, html)

joto_obj.delete_req()
joto_obj.create_req()
joto_obj.check_req()

# Flask
# ------------------------------------------------------------------------------
UPLOAD_FOLDER = 'test_workspace/upload'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route("/", methods=['GET', 'POST'])
def upload_file():
# def index():
    if request.method == 'POST':
        date = request.form['date']
        comment = request.form['comment']

        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            print("filename: ", filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('download_file', name=filename))        print("date from form: ", date)
            # return redirect(url_for('download_file', name=filename))

        joto_obj.add_new_entry(date, comment, 'test_workspace/upload/'+filename)
        joto_obj.create_content()
        joto_obj.write_content()

    elif request.method == 'GET':
        pass
    #    return render_template('index.html', form=form)
    
    return render_template("new_entry.html")

