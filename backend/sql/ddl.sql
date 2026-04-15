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
    full_content LONGTEXT NULL,
    article_url VARCHAR(1000) NOT NULL,
    image_url VARCHAR(1000) NULL,
    summary TEXT NULL,
    crawl_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    summary_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT NULL,
    published_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_news_article_url UNIQUE (article_url)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------
-- index (성능)
-- ------------------------
CREATE INDEX idx_messages_session_id ON messages(agent_session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

CREATE INDEX idx_news_created_at ON news(created_at);
CREATE INDEX idx_news_published_at ON news(published_at);
CREATE INDEX idx_news_crawl_status ON news(crawl_status);


SET FOREIGN_KEY_CHECKS = 1;