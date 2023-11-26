from flask import Flask, render_template, request, abort, redirect, url_for
from werkzeug.utils import secure_filename
import os,sys,inspect
import joto
from datetime import datetime

# Test Setup
# ------------------------------------------------------------------------------
# load config and setup objects
if os.path.isfile("test_config.json"):
    json_config = joto.JsonConfig("test_config.json")
else:
    print("Missing config file")
    exit() 

sqlite_db = joto.JotoSQLiteDB(json_config)
images_manage = joto.ImagesManage(json_config)
html = joto.HTML("./templates/output.html", json_config)
joto_obj = joto.Joto(json_config, sqlite_db, images_manage, html)

joto_obj.delete_req()
joto_obj.create_req()
joto_obj.check_req()

# Flask
# ------------------------------------------------------------------------------
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = joto_obj.images_manage.get_upld_dir()
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
        else:
            filename = ""

        new_entry_status = False
        if joto_obj.add_new_entry(date, comment, filename):
            new_entry_status = True
        joto_obj.create_content()
        joto_obj.write_content()
        
        if new_entry_status:
            return redirect(url_for('new_entry_complete'))
        else:
            return redirect(url_for('new_entry_failure'))

    elif request.method == 'GET':
        pass
    #    return render_template('index.html', form=form)

    today_date = datetime.today().strftime('%Y-%m-%d')
    return render_template("new_entry.html", today_date=today_date)

@app.route("/new_entry_complete")
def new_entry_complete():
    return render_template("new_entry_complete.html")

@app.route("/new_entry_failure")
def new_entry_failure():
    return render_template("new_entry_failure.html")

