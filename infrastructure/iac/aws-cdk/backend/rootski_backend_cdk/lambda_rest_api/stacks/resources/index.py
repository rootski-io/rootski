from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse
from mangum import Mangum

API_VERSION = "v1"

router = APIRouter()


def root():
    return RedirectResponse("/docs")


router.get("/")(root)


# @router.get("/environment-variables")
# def get_environment_variables():
#     return dict(os.environ)


@router.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


app = FastAPI(
    title="Test FastAPI with AWS CDK, API Gateway, and Lambda.",
    terms_of_service="Gotta catch 'em all.",
    # all routes will be prefixed with this path
    version=API_VERSION,
)

app.include_router(router, prefix=f"/api/{API_VERSION}")
app.get("/")(root)

handler = Mangum(app)
