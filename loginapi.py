from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr

# Initialize FastAPI app
app = FastAPI()

# Mock user data (replace with a proper database in real-world scenarios)
users = {
    "hvfhsbfjsjfjsbfjsbfjb@gmail.com": "641154612",
    "user2@example.com": "securepassword",
}
 
# Define request model
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Login endpoint
@app.post("/login")
async def login(request: LoginRequest):
    # Check if the email exists
    if request.email not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email is not registered"
        )
    # Check if the password matches
    if users[request.email] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password"
        )
    # If successful
    return {"message": "Login successfully"}

# Run the app with: uvicorn filename:app --reload
