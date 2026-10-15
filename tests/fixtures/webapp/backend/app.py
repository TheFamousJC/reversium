from . import models
from .models import User
import missing_library


@app.get(
    '/users'
)
def users():
    return []
