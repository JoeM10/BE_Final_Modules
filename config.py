import os

MYSQL_PASSWORD = os.getenv('MYSQL_PASS')

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://root:{MYSQL_PASSWORD}@localhost/mechanic_shop_db'
    DEBUG = True

class TestingConfig:
    pass

class ProductionConfig:
    pass