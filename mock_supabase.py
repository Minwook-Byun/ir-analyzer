"""
MYSC IR Platform - Mock Supabase Server
실제 Supabase 대신 로컬에서 REST API 시뮬레이션
"""
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Mock 데이터베이스 (메모리 저장)
mock_db = {
    "users": [],
    "analysis_projects": [],
    "analysis_results": [],
    "conversation_sessions": [],
    "conversation_messages": [],
    "api_usage": []
}

app = FastAPI(title="Mock Supabase", port=54321)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Mock Supabase API Server", "tables": len(mock_db)}

# 사용자 테이블
@app.post("/rest/v1/users")
async def create_user(request: Request):
    data = await request.json()
    user = {
        "id": str(uuid.uuid4()),
        "email": data.get("email"),
        "api_key_hash": data.get("api_key_hash"),
        "created_at": datetime.utcnow().isoformat(),
        "last_login": data.get("last_login", datetime.utcnow().isoformat()),
        "settings": {}
    }
    mock_db["users"].append(user)
    return [user]

@app.get("/rest/v1/users")
async def get_users(email: str = None):
    if email:
        users = [u for u in mock_db["users"] if u["email"] == email]
        return users
    return mock_db["users"]

# 분석 프로젝트 테이블
@app.post("/rest/v1/analysis_projects")
async def create_project(request: Request):
    data = await request.json()
    project = {
        "id": data.get("id") or str(uuid.uuid4()),
        "user_id": data.get("user_id"),
        "company_name": data.get("company_name"),
        "file_names": data.get("file_names", []),
        "file_contents": data.get("file_contents"),
        "status": data.get("status", "pending"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    mock_db["analysis_projects"].append(project)
    return [project]

@app.patch("/rest/v1/analysis_projects")
async def update_project(request: Request, id: str):
    data = await request.json()
    for i, project in enumerate(mock_db["analysis_projects"]):
        if project["id"] == id:
            project.update(data)
            project["updated_at"] = datetime.utcnow().isoformat()
            return [project]
    return []

# 분석 결과 테이블
@app.post("/rest/v1/analysis_results")
async def create_analysis_result(request: Request):
    data = await request.json()
    result = {
        "id": str(uuid.uuid4()),
        "project_id": data.get("project_id"),
        "section_type": data.get("section_type"),
        "content": data.get("content"),
        "tokens_used": data.get("tokens_used", 0),
        "processing_time_ms": 0,
        "created_at": datetime.utcnow().isoformat()
    }
    mock_db["analysis_results"].append(result)
    return [result]

@app.get("/rest/v1/analysis_results")
async def get_analysis_results(project_id: str = None):
    if project_id:
        results = [r for r in mock_db["analysis_results"] if r["project_id"] == project_id]
        return sorted(results, key=lambda x: x["created_at"])
    return mock_db["analysis_results"]

# 대화 세션 테이블
@app.post("/rest/v1/conversation_sessions")
async def create_conversation_session(request: Request):
    data = await request.json()
    session = {
        "id": data.get("id") or str(uuid.uuid4()),
        "project_id": data.get("project_id"),
        "user_id": data.get("user_id"),
        "session_name": data.get("session_name"),
        "created_at": datetime.utcnow().isoformat(),
        "last_message_at": datetime.utcnow().isoformat()
    }
    mock_db["conversation_sessions"].append(session)
    return [session]

# 대화 메시지 테이블
@app.post("/rest/v1/conversation_messages")
async def create_conversation_message(request: Request):
    data = await request.json()
    message = {
        "id": str(uuid.uuid4()),
        "session_id": data.get("session_id"),
        "message_type": data.get("message_type"),
        "content": data.get("content"),
        "metadata": data.get("metadata", {}),
        "created_at": datetime.utcnow().isoformat()
    }
    mock_db["conversation_messages"].append(message)
    return [message]

@app.get("/rest/v1/conversation_messages")
async def get_conversation_messages(session_id: str = None):
    if session_id:
        messages = [m for m in mock_db["conversation_messages"] if m["session_id"] == session_id]
        return sorted(messages, key=lambda x: x["created_at"])
    return mock_db["conversation_messages"]

# 디버그 엔드포인트
@app.get("/debug/db")
async def debug_db():
    return {
        "tables": {table: len(data) for table, data in mock_db.items()},
        "data": mock_db
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Mock Supabase starting on http://localhost:54321")
    print("📊 Dashboard: http://localhost:54321/debug/db")
    uvicorn.run(app, host="0.0.0.0", port=54321)