from flask import Blueprint
from flask_httpauth import HTTPTokenAuth
from spectree import SpecTree
from pydantic import BaseModel, Field, constr
from flask_httpauth import HTTPTokenAuth
from spectree import SpecTree, SecurityScheme




api = Blueprint("api", __name__, url_prefix="/api")
spec = SpecTree("flask", annotations=True)


spec = SpecTree("flask", annotations=True)

@api.route("/api/user", methods=["POST"])
@spec.validate(tags=["api"])
def user_profile(json: Profile):
    print(json)
    return {"text": "it works"}


spec = SpecTree(
"flask",
security_schemes=[
SecurityScheme(
name="bearer_token",
data={"type": "http", "scheme": "bearer"}
)
],
security=[{"bearer_token": []}]
)






class Profile(BaseModel):
    name: str = Field(min_length=2, max_length=40)
    age: int = Field(gt=0, lt=150)



auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
"secret-token-1": "john",
"secret-token-2": "susan"
}





@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]

@api.route('/')
@auth.login_required
def index():
    return "Hello, {}!".format(auth.current_user())


