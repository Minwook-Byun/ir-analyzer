-- MYSC IR Platform - Supabase Database Schema
-- 이 스크립트를 Supabase SQL Editor에서 실행하세요

-- 1. Users 테이블 (사용자 정보)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    api_key_hash VARCHAR(255), -- 암호화된 Gemini API 키
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb
);

-- 2. Analysis Projects 테이블 (분석 프로젝트)
CREATE TABLE analysis_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    file_names TEXT[], -- 업로드된 파일명들
    file_contents TEXT, -- 파일 내용 (Base64 인코딩)
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Analysis Results 테이블 (분석 결과 저장)
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES analysis_projects(id) ON DELETE CASCADE,
    section_type VARCHAR(50) NOT NULL, -- 'executive_summary', 'financial', 'market', etc.
    content JSONB NOT NULL, -- 분석 결과 JSON
    tokens_used INTEGER DEFAULT 0,
    processing_time_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Conversation Sessions 테이블 (대화 세션)
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES analysis_projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Conversation Messages 테이블 (대화 메시지)
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'ai', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb, -- 추가 정보 (토큰 수, 분석 타입 등)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. API Usage Tracking 테이블 (API 사용량 추적)
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES analysis_projects(id) ON DELETE SET NULL,
    api_type VARCHAR(50) NOT NULL, -- 'gemini', 'analysis', 'conversation'
    tokens_used INTEGER NOT NULL,
    cost_usd DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_projects_user_id ON analysis_projects(user_id);
CREATE INDEX idx_projects_created_at ON analysis_projects(created_at);
CREATE INDEX idx_results_project_id ON analysis_results(project_id);
CREATE INDEX idx_results_section_type ON analysis_results(section_type);
CREATE INDEX idx_sessions_project_id ON conversation_sessions(project_id);
CREATE INDEX idx_messages_session_id ON conversation_messages(session_id);
CREATE INDEX idx_messages_created_at ON conversation_messages(created_at);
CREATE INDEX idx_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_usage_created_at ON api_usage(created_at);

-- Updated_at 트리거 함수 생성
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Analysis Projects에 updated_at 트리거 적용
CREATE TRIGGER update_analysis_projects_updated_at 
    BEFORE UPDATE ON analysis_projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Conversation Sessions의 last_message_at 업데이트 트리거
CREATE OR REPLACE FUNCTION update_session_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation_sessions 
    SET last_message_at = NEW.created_at 
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_session_on_new_message
    AFTER INSERT ON conversation_messages
    FOR EACH ROW EXECUTE FUNCTION update_session_last_message();

-- Row Level Security (RLS) 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- 기본 RLS 정책 (사용자는 자신의 데이터만 접근 가능)
-- 실제 JWT 토큰 기반 인증 정책은 추후 설정
CREATE POLICY "Users can view their own data" ON users
    FOR ALL USING (true); -- 임시로 모든 접근 허용, 추후 JWT 기반으로 수정

CREATE POLICY "Users can view their own projects" ON analysis_projects
    FOR ALL USING (true);

CREATE POLICY "Users can view their own results" ON analysis_results
    FOR ALL USING (true);

CREATE POLICY "Users can view their own sessions" ON conversation_sessions
    FOR ALL USING (true);

CREATE POLICY "Users can view their own messages" ON conversation_messages
    FOR ALL USING (true);

CREATE POLICY "Users can view their own usage" ON api_usage
    FOR ALL USING (true);

-- 초기 데이터 삽입 (테스트용)
INSERT INTO users (email, api_key_hash) VALUES 
('test@mysc.com', 'test_hash_placeholder');

COMMENT ON TABLE users IS 'MYSC IR Platform 사용자 정보';
COMMENT ON TABLE analysis_projects IS 'IR 분석 프로젝트 정보';
COMMENT ON TABLE analysis_results IS 'AI 분석 결과 저장';
COMMENT ON TABLE conversation_sessions IS '사용자-AI 대화 세션';
COMMENT ON TABLE conversation_messages IS '대화 메시지 내역';
COMMENT ON TABLE api_usage IS 'API 사용량 및 비용 추적';