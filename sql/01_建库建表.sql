-- ============================================================
--  第 1 步：建库 + 建表（从零重来版）
--  库：usedbooks      表：books
--  环境：openEuler + MySQL 8.x
-- ------------------------------------------------------------
--  两种用法：
--    A. 登进 MySQL 后，按【A】【B】【C】三段分别粘贴
--    B. 整个文件一次跑完：  mysql -uroot -p < 01_建库建表.sql
-- ------------------------------------------------------------
--  ⚠️ 铁律：每条语句必须以英文分号 ; 结尾
--     忘了分号 → 提示符变成  ->   这时补分号回车，或按 Ctrl+C 放弃
-- ============================================================


-- ============================================================
-- 【A】清场 + 建库 + 选库
-- ============================================================

-- ---------- A1. 清场 ----------
-- DROP DATABASE = 把整个库连表带数据一起删掉，不可恢复、没有回收站
-- IF EXISTS     = 库不存在时不报错（让脚本能反复跑，不会中断）
-- ⚠️ 上次建的 books 表和里面的数据会一起没，这是故意的一步
DROP DATABASE IF EXISTS usedbooks;

-- ---------- A2. 建库 ----------
-- CREATE DATABASE 库名  = 造一个空仓库，此刻里面什么都没有
--   CHARACTER SET utf8mb4  字符集：能存中文 + emoji
--                          （只写 utf8 是 MySQL 的残缺版，存不了 emoji，永远别用）
--   COLLATE utf8mb4_0900_ai_ci  比较规则：ai = 大小写不敏感，ci = 不区分大小写
--                          （'ABC' 和 'abc' 会被当成相等，符合日常直觉）
CREATE DATABASE usedbooks
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- ---------- A3. 选库 ----------
-- USE = 告诉 MySQL「接下来所有操作都作用在这个库上」
-- 忘写这行的后果：ERROR 1046 No database selected
USE usedbooks;


-- ============================================================
-- 【B】建表
-- ============================================================

-- 先删同名旧表（库刚建是空的，这句实际上是保险，方便单独重跑本段）
DROP TABLE IF EXISTS books;

-- 语法骨架：
--   CREATE TABLE 表名 (
--     列名  数据类型  [约束]  [COMMENT '中文说明'],
--     ...
--     PRIMARY KEY (列名)
--   ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='表说明';
--
-- 三个常用约束：
--   NOT NULL        这一列不能为空（不写就能为 NULL）
--   DEFAULT 值      不给值时自动填什么
--   AUTO_INCREMENT  自增，只能用在主键/索引列上，每插一行 +1
--   COMMENT 'xxx'   给列写中文备注，敲 DESC books; 时能看到，强烈建议写
--
-- ⚠️ condition 是 MySQL 保留字（它自己有含义），当列名必须加 反引号 `condition`
--    （反引号在键盘左上角 Esc 下面那个键，不是单引号）
CREATE TABLE books (
  id          INT UNSIGNED   NOT NULL AUTO_INCREMENT COMMENT '主键，自动编号',
  title       VARCHAR(120)   NOT NULL                COMMENT '书名',
  author      VARCHAR(60)    DEFAULT NULL            COMMENT '作者',
  price       DECIMAL(6,2)   NOT NULL DEFAULT 0.00   COMMENT '售价，单位元',
  `condition` ENUM('new','good','fair','poor')
                             NOT NULL DEFAULT 'good' COMMENT '品相：全新/良好/一般/较差',
  seller      VARCHAR(40)    DEFAULT NULL            COMMENT '卖家昵称',
  is_sold     TINYINT        NOT NULL DEFAULT 0      COMMENT '是否售出：0否 1是',
  listed_at   DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上架时间',
  PRIMARY KEY (id),
  KEY idx_seller (seller),
  KEY idx_price  (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='二手书表';

-- 说明：
--   · TINYINT 不写 (1)。以前写 TINYINT(1) 会报 Warning 1681（显示宽度已弃用），
--     去掉括号就没有警告，存储空间一样是 1 字节。
--   · ENGINE=InnoDB 是事务型引擎，支持事务/行锁/外键，8.0 默认就是它，写上是明确态度。
--   · KEY idx_seller / idx_price 是普通索引，给以后 WHERE seller=... 这类查询加速。
--     现阶段记一句：索引 = 书的目录，查得快但写起来稍慢，不是越多越好。


-- ============================================================
-- 【C】验证：确认库和表真的建成了
-- ============================================================

SHOW DATABASES;                          -- 列表里要有 usedbooks
SHOW TABLES;                             -- 要有 books（在 USE 之后才有效）
DESC books;                              -- 打印 8 行字段结构，确认列名和类型
SELECT COUNT(*) AS 当前册数 FROM books;  -- 应为 0：表是空的，还没插数据


-- ============================================================
--  预期结果对照表
-- ------------------------------------------------------------
--  A1 DROP    → Query OK, 0 rows affected
--  A2 CREATE  → Query OK, 1 row affected
--  A3 USE     → Database changed
--  B  CREATE  → Query OK, 0 rows affected
--  C  SHOW TABLES → 一行 books
--  C  DESC books  → 8 行（Field/Type/Null/Key/Default/Extra）
--  C  COUNT(*)    → 0
-- ============================================================
