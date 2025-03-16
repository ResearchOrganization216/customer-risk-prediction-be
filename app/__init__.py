from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Loading configuration
    app.config.from_object('app.config.Config')

    # Initializing extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Registering blueprints
    from app.routes.customer_risk_prediction.customer_risk_prediction import customer_risk_bp
    from app.routes.customer_risk_agent.risk_routes import risk_bp
    from app.routes.customer_risk_assesment_llama.risk_assesment_llama import risk_assesment_llama_bp
    from app.routes.customer_risk_assesment_openai.risk_assesment_openai import risk_assessment_openai_bp


    app.register_blueprint(customer_risk_bp, url_prefix='/api')
    app.register_blueprint(risk_bp, url_prefix='/api') #new route for risk assesment using Agent
    app.register_blueprint(risk_assesment_llama_bp, url_prefix='/api') #new route for risk assesment using
    app.register_blueprint(risk_assessment_openai_bp, url_prefix='/api') #new route for risk assesment using OpenAI

    # Default route for '/'
    @app.route('/')
    def index():
        return "Welcome to Flask with PostgreSQL!"

    return app
