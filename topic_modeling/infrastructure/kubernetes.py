from fastapi import APIRouter
from fastapi import FastAPI

router = APIRouter()
app = FastAPI(debug=True)

'''
Endpoint for Kubernetes to get health status

We can still improve it!
'''
@router.get('/healthz', status_code=200)
async def health_check():
    return {"status": "UP"}


@router.get('/ready', status_code=200)
async def ready_check():
    return {"ready": True}


@router.get('/info', status_code=200)
async def info_endpoint():
    return {'app': {'name': 'keycloak-service', 'version': '0.0.1-alpha.0'}}
