-- 可选：空库手工执行；会 DROP 重建表并插入示例数据，有数据勿用。

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS user_favorite;
DROP TABLE IF EXISTS user_token;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS news;
DROP TABLE IF EXISTS news_category;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE news_category (
  id INT NOT NULL AUTO_INCREMENT COMMENT '分类ID',
  name VARCHAR(50) NOT NULL COMMENT '分类名称',
  sort_order INT NOT NULL DEFAULT 0 COMMENT '排序',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE news (
  id INT NOT NULL AUTO_INCREMENT COMMENT '新闻ID',
  title VARCHAR(255) NOT NULL COMMENT '新闻标题',
  description VARCHAR(500) DEFAULT NULL COMMENT '新闻简介',
  content TEXT NOT NULL COMMENT '新闻内容',
  image VARCHAR(255) DEFAULT NULL COMMENT '封面图片URL',
  author VARCHAR(50) DEFAULT NULL COMMENT '作者',
  category_id INT NOT NULL COMMENT '分类ID',
  views INT NOT NULL DEFAULT 0 COMMENT '浏览量',
  publish_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY fk_news_category_idx (category_id),
  KEY idx_publish_time (publish_time),
  CONSTRAINT fk_news_category FOREIGN KEY (category_id) REFERENCES news_category (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user` (
  id INT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  username VARCHAR(50) NOT NULL COMMENT '用户名',
  password VARCHAR(255) NOT NULL COMMENT '密码(加密储存)',
  nickname VARCHAR(50) DEFAULT NULL COMMENT '昵称',
  avatar VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
  gender ENUM('male','female','unknown') DEFAULT NULL COMMENT '性别',
  bio VARCHAR(500) DEFAULT '这个人很懒，什么都没有留下' COMMENT '个人简介',
  phone VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY username_UNIQUE (username),
  UNIQUE KEY phone_UNIQUE (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_token (
  id INT NOT NULL AUTO_INCREMENT COMMENT '令牌ID',
  user_id INT NOT NULL COMMENT '用户ID',
  token VARCHAR(255) NOT NULL COMMENT '令牌值',
  expires_at DATETIME NOT NULL COMMENT '过期时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY token_UNIQUE (token),
  KEY fk_user_token_user_idx (user_id),
  CONSTRAINT fk_user_token_user FOREIGN KEY (user_id) REFERENCES `user` (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_favorite (
  id INT NOT NULL AUTO_INCREMENT COMMENT '收藏记录ID',
  user_id INT NOT NULL COMMENT '用户ID',
  news_id INT NOT NULL COMMENT '新闻ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_news_favorite (user_id, news_id),
  KEY idx_user_favorite_user_id (user_id),
  KEY idx_user_favorite_news_id (news_id),
  CONSTRAINT fk_user_favorite_user FOREIGN KEY (user_id) REFERENCES `user` (id) ON DELETE CASCADE,
  CONSTRAINT fk_user_favorite_news FOREIGN KEY (news_id) REFERENCES news (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO news_category (id, name, sort_order) VALUES
  (1, '科技', 1),
  (2, '生活', 2);

INSERT INTO news (id, title, description, content, image, author, category_id, views, publish_time) VALUES
  (1, '欢迎使用本新闻示例', '示例数据', '这是一条可选的示例新闻，便于空库联调。', NULL, '系统', 1, 0, NOW()),
  (2, '生活小贴士：规律作息', '保持健康节奏', '保证睡眠、适量运动，有助于提升学习与工作效率。', NULL, '编辑部', 2, 3, NOW()),
  (3, '科技速览：异步与数据库', 'FastAPI 与 MySQL', '使用异步数据库驱动可以在 I/O 等待时处理更多并发请求。', NULL, '编辑部', 1, 10, NOW());

-- 演示账号：用户名 demo，密码 demo123（bcrypt）
INSERT INTO `user` (id, username, password, nickname) VALUES (
  1,
  'demo',
  '$2b$12$jagF1SuEia3TIY/fpjZ9hunED3Ns5Ru4hMp0sl1U6GiIc5Cg1CJz2',
  '演示用户'
);
