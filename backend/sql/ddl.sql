-- 문자셋 설정 (한글 + 이모지 대응)
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------
-- agent_sessions
-- ------------------------
CREATE TABLE IF NOT EXISTS agent_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------
-- messages
-- ------------------------
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_session_id INT NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_messages_session
        FOREIGN KEY (agent_session_id)
        REFERENCES agent_sessions(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description VARCHAR(1000) NULL,                                   -- 네이버 API 요약 description
    full_content LONGTEXT NULL,                           -- 크롤링한 본문 전체
    link VARCHAR(1000) NULL,                                       -- 네이버 뉴스 URL
    original_link TEXT NULL,                              -- 원본 언론사 URL
    image_url VARCHAR(1000) NULL,                                  -- 대표 이미지
    summary TEXT NULL,                                    -- LLM 요약 결과 (나중에 채움)
    crawl_status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- success / failed / pending
    summary_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT NULL,
    pub_date DATETIME NULL,                               -- 네이버 API pubDate
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------
-- index (성능)
-- ------------------------
CREATE INDEX idx_messages_session_id ON messages(agent_session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

CREATE INDEX idx_news_created_at ON news(created_at);
CREATE INDEX idx_news_pub_date ON news(pub_date);
CREATE INDEX idx_news_crawl_status ON news(crawl_status);

CREATE INDEX idx_news_session_id ON news(agent_session_id);

SET FOREIGN_KEY_CHECKS = 1;