
CREATE TABLE IF NOT EXISTS `user_favorite` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '收藏记录ID',
  `user_id` int unsigned NOT NULL COMMENT '用户ID',
  `news_id` int unsigned NOT NULL COMMENT '新闻ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_news_favorite` (`user_id`,`news_id`),
  KEY `idx_user_favorite_user_id` (`user_id`),
  KEY `idx_user_favorite_news_id` (`news_id`),
  CONSTRAINT `fk_user_favorite_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_favorite_news` FOREIGN KEY (`news_id`) REFERENCES `news` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户新闻收藏';
