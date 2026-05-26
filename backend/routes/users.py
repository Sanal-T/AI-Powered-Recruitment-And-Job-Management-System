# In backend/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend import auth, models  # CORRECTED IMPORT

router = APIRouter()

# This is a fake user database for demonstration.
# In a real app, you would get users from your MongoDB.
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": auth.get_password_hash("password"), # Hashed version of "password"
        "role": "admin",
    },
    "candidate": {
        "username": "candidate",
        "hashed_password": auth.get_password_hash("password"), # Hashed version of "password"
        "role": "candidate",
    }
}

@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS_DB.get(form_data.username)
    if not user or not auth.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}