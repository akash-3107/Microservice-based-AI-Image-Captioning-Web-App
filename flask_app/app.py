from flask import Flask, render_template, request
import requests
from models import db, CaptionLog


app = Flask(__name__)

# update database details
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///captions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


FASTAPI_URL = "http://localhost:8000/caption"


@app.before_request
def create_tables():
    db.create_all()



@app.route('/', methods = ['GET','POST'])
def index():
    caption = None
    if request.method == "POST":
        image = request.files["image"]
        files = {"file": (image.filename, image.stream, image.content_type)}
        response = requests.post(FASTAPI_URL, files=files)
        caption = response.json().get("caption")

        # log to the database
        log = CaptionLog(image_name=image.filename, caption=caption)
        db.session.add(log)
        db.session.commit()

    return render_template("index.html", caption=caption)


@app.route("/history")
def history():
    logs = CaptionLog.query.order_by(CaptionLog.timestamp.desc()).all()
    return render_template("history.html", logs=logs)


if __name__ == "__main__":
    app.run(debug=True)