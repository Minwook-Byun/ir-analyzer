from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse(content="""
    <html>
        <head><title>IR Analyzer - Simple Test</title></head>
        <body>
            <h1>🚀 IR Analyzer is Working!</h1>
            <p>Investment Report Analysis Platform</p>
            <p>Status: ✅ Server is running successfully</p>
        </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Simple FastAPI app is working"}