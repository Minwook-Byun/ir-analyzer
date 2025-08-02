from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """A simple endpoint to test deployment."""
    return HTMLResponse(content="<h1>Deployment Test Successful!</h1><p>The basic FastAPI app is running correctly on Vercel.</p>")

# All other code is temporarily removed for debugging.
