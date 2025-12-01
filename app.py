from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager
from routes import register_routes
from markupsafe import Markup

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# jinja filter to convert new lines to <br>
@app.template_filter('nl2br')
def nl2br_filter(s):
    if not s:
        return ''
    return Markup(s.replace('\n', '<br>'))

register_routes(app)

# create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
