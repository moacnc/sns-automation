-- Instagram Automation 데이터베이스 초기화 스크립트
-- Docker Compose로 PostgreSQL 시작 시 자동 실행됨

-- 세션 테이블
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    device_id VARCHAR(255),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(50),
    total_interactions INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_follows INTEGER DEFAULT 0,
    total_unfollows INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 세션 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_sessions_username ON sessions(username);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);

-- 인터랙션 테이블
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    target_user VARCHAR(255),
    target_post VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    duration_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

-- 인터랙션 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_action ON interactions(action);
CREATE INDEX IF NOT EXISTS idx_interactions_status ON interactions(status);

-- 통계 테이블
CREATE TABLE IF NOT EXISTS statistics (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    total_likes INTEGER DEFAULT 0,
    total_follows INTEGER DEFAULT 0,
    total_unfollows INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    sessions_count INTEGER DEFAULT 0,
    success_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, date)
);

-- 통계 테이블 인덱스
CREATE INDEX IF NOT EXISTS idx_statistics_username_date ON statistics(username, date DESC);

-- ===== 스토리 리스토리 관련 테이블 =====

-- 리스토리 세션 테이블
CREATE TABLE IF NOT EXISTS restory_sessions (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    device_id VARCHAR(255),
    target_hashtags TEXT[] NOT NULL,  -- 검색 대상 해시태그 배열
    max_count INTEGER NOT NULL,       -- 최대 수집 개수
    total_viewed INTEGER DEFAULT 0,   -- 총 조회한 스토리 수
    total_restoried INTEGER DEFAULT 0, -- 성공한 리스토리 수
    total_filtered INTEGER DEFAULT 0,  -- 필터링된 스토리 수
    filter_settings JSONB,            -- 필터링 설정 (bad_words 등)
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'running', -- running, completed, failed
    error_message TEXT,
    metadata JSONB,                   -- 추가 메타데이터
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 리스토리 세션 인덱스
CREATE INDEX IF NOT EXISTS idx_restory_sessions_username ON restory_sessions(username);
CREATE INDEX IF NOT EXISTS idx_restory_sessions_start_time ON restory_sessions(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_restory_sessions_status ON restory_sessions(status);
CREATE INDEX IF NOT EXISTS idx_restory_sessions_hashtags ON restory_sessions USING GIN(target_hashtags);

-- 필터링된 스토리 테이블
CREATE TABLE IF NOT EXISTS filtered_stories (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    story_id VARCHAR(255) NOT NULL,   -- Instagram 스토리 ID
    username VARCHAR(255) NOT NULL,   -- 스토리 작성자
    text TEXT,                        -- 스토리 텍스트 내용
    image_path VARCHAR(500),          -- 스크린샷 경로
    url VARCHAR(500),                 -- 스토리 딥링크 URL
    filter_reason VARCHAR(50) NOT NULL, -- bad_word, spam, adult_content, etc.
    filter_action VARCHAR(50) NOT NULL, -- skip, warn, block
    bad_words_found TEXT[],           -- 발견된 불량 단어 배열
    confidence REAL,                  -- 필터링 신뢰도 (0.0 ~ 1.0)
    moderation_result JSONB,          -- OpenAI Moderation API 결과
    filter_details TEXT,              -- 필터링 상세 내용
    timestamp TIMESTAMP NOT NULL,     -- 스토리 수집 시각
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES restory_sessions(session_id) ON DELETE CASCADE
);

-- 필터링된 스토리 인덱스
CREATE INDEX IF NOT EXISTS idx_filtered_stories_session ON filtered_stories(session_id);
CREATE INDEX IF NOT EXISTS idx_filtered_stories_username ON filtered_stories(username);
CREATE INDEX IF NOT EXISTS idx_filtered_stories_reason ON filtered_stories(filter_reason);
CREATE INDEX IF NOT EXISTS idx_filtered_stories_timestamp ON filtered_stories(timestamp DESC);

-- 리스토리 결과 테이블
CREATE TABLE IF NOT EXISTS restory_results (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    story_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    text TEXT,
    image_path VARCHAR(500),
    url VARCHAR(500),
    success BOOLEAN NOT NULL,         -- 리스토리 성공 여부
    error_message TEXT,               -- 실패 시 에러 메시지
    duration_ms INTEGER,              -- 리스토리 소요 시간 (밀리초)
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES restory_sessions(session_id) ON DELETE CASCADE
);

-- 리스토리 결과 인덱스
CREATE INDEX IF NOT EXISTS idx_restory_results_session ON restory_results(session_id);
CREATE INDEX IF NOT EXISTS idx_restory_results_success ON restory_results(success);
CREATE INDEX IF NOT EXISTS idx_restory_results_timestamp ON restory_results(timestamp DESC);

-- 초기 데이터 (선택사항)
-- INSERT INTO sessions (session_id, username, start_time, status)
-- VALUES ('initial-session', 'test_user', NOW(), 'completed');

-- 권한 설정 (필요시)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE 'Instagram Automation 데이터베이스 초기화 완료!';
END $$;
