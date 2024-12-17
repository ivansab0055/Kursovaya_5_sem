from flask_restful import Api

from api import __version__
from api.file_management import CreateFoldersApi
from api.restful_api import PredictApi, StatusApi, ResultApi, StopJobApi


def initialize_routes(api: Api):
    api.add_resource(CreateFoldersApi, f'/api/file_management/v{__version__}/create')
    api.add_resource(PredictApi, f'/api/pd/v{__version__}/predict')
    api.add_resource(StatusApi, f'/api/pd/v{__version__}/status')
    api.add_resource(ResultApi, f'/api/pd/v{__version__}/result')
    api.add_resource(StopJobApi, f'/api/pd/v{__version__}/stop')
