-- ----------------------------
-- Table structure for live_num
-- ----------------------------
DROP TABLE IF EXISTS "live_num";
CREATE TABLE "live_num" (
  "id" INTEGER NOT NULL DEFAULT '' PRIMARY KEY AUTOINCREMENT,
  "get_time" TEXT NOT NULL,
  "douyu" integer NOT NULL,
  "huya" integer NOT NULL
);