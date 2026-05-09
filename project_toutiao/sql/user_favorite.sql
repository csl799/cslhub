-- 用户新闻收藏表（在 news_app 库中执行一次）
--
-- MySQL 8 错误 3780：外键两边的列必须「类型一致」——常见是有符号 INT 引用无符号 INT UNSIGNED（或 BIGINT 对 INT 等）。
-- 若仍报错，请先执行：
--   SHOW CREATE TABLE `user`;
--   SHOW CREATE TABLE `news`;
-- 将下面 user_id、news_id 的类型改成与 `user`.`id`、`news`.`id` 完全一致（含 UNSIGNED、BIGINT 等）。
--
-- 若表已错误创建过，可先：DROP TABLE IF EXISTS `user_favorite`;

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
