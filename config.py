import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vss'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://admin001:admin001@testdb001.caruphjxuyij.ap-northeast-2.rds.amazonaws.com/testdb001'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
    DB_NAME = os.environ.get('DB_NAME') or 'testdb001'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
