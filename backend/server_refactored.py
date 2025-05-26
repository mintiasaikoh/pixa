#!/usr/bin/env python3
"""
Pixa - AIピクセルアート生成アプリケーション
リファクタリング後のメインサーバー
"""

import logging
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# 設定とサービスのインポート
from config.settings import Config
from services.ai_service import ai_service
from routes.basic_routes import basic_routes
from routes.animation_routes import animation_routes

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Flaskアプリケーションファクトリ"""
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    # CORS設定
    CORS(app)
    
    # 設定の適用
    app.config.from_object(config_class)
    
    # Blueprintの登録
    app.register_blueprint(basic_routes, url_prefix='/api')
    app.register_blueprint(animation_routes, url_prefix='/api')
    
    # 静的ファイル配信
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)
    
    # エラーハンドラー
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return {'error': 'Internal Server Error'}, 500
    
    # アプリケーション初期化
    with app.app_context():
        # AI サービスの初期化
        if not ai_service.initialize_pipeline():
            logger.warning("AI service initialization failed")
        else:
            logger.info("AI service initialized successfully")
    
    return app


def main():
    """メイン実行関数"""
    try:
        # アプリケーション作成
        app = create_app()
        
        # サーバー設定
        host = app.config.get('HOST', '0.0.0.0')
        port = app.config.get('PORT', 5001)
        debug = app.config.get('DEBUG', False)
        
        logger.info(f"Starting Pixa server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        # サーバー起動
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()
