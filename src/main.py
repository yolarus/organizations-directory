import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from src.activities.routers import activity_router
from src.activities.urls import activity_url
from src.buildings.routers import building_router
from src.buildings.urls import building_url
from src.config.settings import project_config
from src.organizations.routers import organization_router
from src.organizations.urls import organization_url

DEBUG = project_config.app.DEBUG

SWAGGER_UI_SETTINGS = {
    'filter': True,
    'persistAuthorization': True,
    'deepLinking': True,
    'displayRequestDuration': True,
    'tryItOutEnabled': True,
    'syntaxHighlight': True,
    'operationsSorter': 'alpha',
}

app = FastAPI(
    title='Organizations',
    debug=DEBUG,
    docs_url='/api/docs/',
    redoc_url='/api/redoc/',
    swagger_ui_parameters=SWAGGER_UI_SETTINGS,
)

app.include_router(activity_router, prefix=activity_url(), tags=[activity_url.module])
app.include_router(building_router, prefix=building_url(), tags=[building_url.module])
app.include_router(organization_router, prefix=organization_url(), tags=[organization_url.module])

add_pagination(app)


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
