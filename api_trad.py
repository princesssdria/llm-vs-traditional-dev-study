from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 1. Keep your dummy database OUTSIDE of any class
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
    }
}


def fake_hash_password(password: str):
    return "fakehashed" + password


# 2. Your Pydantic model stays clean with just fields
class User(BaseModel):
    username: str
    email: str


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not user["hashed_password"] == fake_hash_password(
        form_data.password
    ):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    return {"access_token": user["username"], "token_type": "bearer"}


@app.post("/users/")
async def create_user(user: User, token: str = Depends(oauth2_scheme)):
    return user