-- sys_config: scalar/json split + optimistic version
-- Author: Charlie
-- Idempotent-ish: ignore duplicate column errors if re-run manually.

ALTER TABLE `sys_config`
  ADD COLUMN `config_json` json NULL COMMENT '复杂配置（JSON：list/object）' AFTER `config_value`;

ALTER TABLE `sys_config`
  ADD COLUMN `version` int NOT NULL DEFAULT 0 COMMENT '乐观锁版本' AFTER `ext_json`;

-- Normalize legacy INT aliases
UPDATE `sys_config`
SET `value_type` = 'NUMBER'
WHERE UPPER(`value_type`) IN ('INT', 'INTEGER', 'LONG');

-- Move JSON-typed (or JSON-looking) scalar text into config_json
UPDATE `sys_config`
SET
  `config_json` = CAST(`config_value` AS JSON),
  `config_value` = NULL,
  `value_type` = 'JSON'
WHERE `config_json` IS NULL
  AND `config_value` IS NOT NULL
  AND `config_value` <> ''
  AND (
    UPPER(`value_type`) = 'JSON'
    OR (
      UPPER(`value_type`) IN ('STRING', 'TEXT')
      AND JSON_VALID(`config_value`)
      AND (
        TRIM(`config_value`) LIKE '{%'
        OR TRIM(`config_value`) LIKE '[%'
      )
    )
  );
