# import os

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY', 'vss')
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'.format(
#         DB_USER=os.environ.get('DB_USER', 'admin001'),
#         DB_PASS=os.environ.get('DB_PASS', 'admin001'),
#         DB_HOST=os.environ.get('DB_HOST', 'placeholder'),
#         DB_NAME=os.environ.get('DB_NAME', 'testdb001')
#     ))
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SESSION_TYPE = 'filesystem'
#     SQLALCHEMY_ENGINE_OPTIONS = {
#         'pool_pre_ping': True,
#         'pool_recycle': 280,
#     }

# class DevelopmentConfig(Config):
#     DEBUG = True
#     SQLALCHEMY_ECHO = False
#     DB_NAME = os.environ.get('DB_NAME', 'testdb001')  # 추가된 부분

# class ProductionConfig(Config):
#     DEBUG = False
#     DB_NAME = os.environ.get('DB_NAME', 'testdb001')  # 추가된 부분

# config = {
#     'development': DevelopmentConfig,
#     'production': ProductionConfig,
#     'default': DevelopmentConfig
# }
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'vss')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://admin001:admin001@testdb001.caruphjxuyij.ap-northeast-2.rds.amazonaws.com/testdb001')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    DB_NAME = os.environ.get('DB_NAME', 'testdb001')  # 추가된 부분

class ProductionConfig(Config):
    DEBUG = False
    DB_NAME = os.environ.get('DB_NAME', 'testdb001')  # 추가된 부분

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
