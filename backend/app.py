from flask import Flask
from flask_cors import CORS
from config import Config
from database import init_db
from routes.recognition import recognition_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    
    init_db()
    
    
    app.register_blueprint(recognition_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {
            "message": "Handwriting Recognition API",
            "status": "running",
            "endpoints": {
                "recognize": "/api/recognize [POST]",
                "download_pdf": "/api/download-pdf [POST]"
            }
        }
    
    @app.route('/health')
    def health():
        return {"status": "healthy"}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)