from flask import Flask
from config import Config
from model.user_model import db
from controller.main_controller import main_controller

app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(main_controller)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
