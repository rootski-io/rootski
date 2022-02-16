from mangum import Mangum

from rootski.main.main import create_app

app = create_app()

handler = Mangum(app)
