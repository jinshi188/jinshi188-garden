-- ============================================================
-- 二手书数据库 练习脚本
-- 用途：openEuler + MySQL 8 建库建表 + CRUD 练习
-- 配套：嵌入式端侧AI / 数据库课程 W2
-- 用法：mysql -uroot -p < usedbooks.sql
-- 注意：所有语句以分号结尾，否则 mysql 会进入 -> 续行状态
-- ============================================================

-- ---------- 1. 建库 ----------
DROP DATABASE IF EXISTS usedbooks;
CREATE DATABASE usedbooks
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE usedbooks;

-- ---------- 2. 建表 ----------
-- condition 是 MySQL 保留字，列名必须用反引号包起来
CREATE TABLE books (
  id          INT UNSIGNED   NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
  title       VARCHAR(120)   NOT NULL                COMMENT '书名',
  author      VARCHAR(60)    DEFAULT NULL            COMMENT '作者',
  price       DECIMAL(6,2)   NOT NULL DEFAULT 0.00   COMMENT '售价，单位元',
  `condition` ENUM('new','good','fair','poor')
                             NOT NULL DEFAULT 'good' COMMENT '品相',
  seller      VARCHAR(40)    DEFAULT NULL            COMMENT '卖家昵称',
  is_sold     TINYINT(1)     NOT NULL DEFAULT 0      COMMENT '是否已售出 0否1是',
  listed_at   DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上架时间',
  PRIMARY KEY (id),
  KEY idx_seller (seller),
  KEY idx_price (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='二手书表';

-- ---------- 3. 增 INSERT ----------
INSERT INTO books (title, author, price, `condition`, seller) VALUES
  ('高等数学 上册',   '同济大学数学系', 12.50, 'good', '张三'),
  ('C 程序设计',      '谭浩强',          8.00, 'fair', '李四'),
  ('算法导论',        'CLRS',           45.00, 'new',  '王五'),
  ('线性代数',        '同济大学数学系',  6.50, 'poor', '张三'),
  ('深入理解计算机系统','Bryant',        68.00, 'good', '王五'),
  ('数据结构与算法分析','Weiss',         25.00, 'fair', '李四');

-- ---------- 4. 查 SELECT ----------
SELECT * FROM books;

SELECT title, price, seller
FROM books
WHERE price < 20
ORDER BY price DESC;

SELECT seller, COUNT(*) AS 册数, ROUND(SUM(price),2) AS 总价
FROM books
GROUP BY seller
ORDER BY 总价 DESC;

SELECT * FROM books WHERE title LIKE '%计算机%';

SELECT * FROM books WHERE `condition` IN ('new','good') AND is_sold = 0;

-- ---------- 5. 改 UPDATE ----------
UPDATE books SET price = 10.00 WHERE id = 2;

UPDATE books SET is_sold = 1, price = 40.00 WHERE title = '算法导论';

SELECT id, title, price, is_sold FROM books WHERE id IN (2,3);

-- ---------- 6. 删 DELETE ----------
-- 铁律：先 SELECT 预览，再 DELETE
SELECT * FROM books WHERE `condition` = 'poor';
DELETE FROM books WHERE `condition` = 'poor';

SELECT COUNT(*) AS 剩余册数 FROM books;

-- ---------- 7. 表结构变更 ALTER ----------
ALTER TABLE books ADD COLUMN contact VARCHAR(60) DEFAULT NULL COMMENT '联系方式';

UPDATE books SET contact = 'wx_zhangsan' WHERE seller = '张三';

SELECT id, title, seller, contact FROM books WHERE contact IS NOT NULL;

-- ---------- 8. 事务（了解即可） ----------
START TRANSACTION;
UPDATE books SET price = price + 1.00 WHERE seller = '李四';
SELECT id, title, price FROM books WHERE seller = '李四';
ROLLBACK;   -- 改成 COMMIT 就是真提交

SELECT id, title, price FROM books WHERE seller = '李四';

-- ---------- 9. 查看结果 ----------
SHOW DATABASES;
SHOW TABLES;
DESC books;
SHOW CREATE TABLE books;

SELECT COUNT(*) AS 最终册数 FROM books;
