from flask import Flask
from config import Config
from model.user_model import db, User
from controller.main_controller import main_controller

app = Flask(__name__, template_folder="view/templates", static_folder="view/static")
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(main_controller)

with app.app_context():
    db.create_all()

    admin_user = User("admin", "admin", "admin")
    db.session.add(admin_user)
    db.session.commit()
    

if __name__ == "__main__":
    app.run(debug=True)
