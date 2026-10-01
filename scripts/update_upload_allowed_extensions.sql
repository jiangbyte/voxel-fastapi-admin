-- 允许上传 .in / .out 等测试数据文件
-- Author: Charlie

UPDATE `sys_config`
SET `config_value` = CASE
    WHEN JSON_CONTAINS(CAST(`config_value` AS JSON), '".in"', '$')
         AND JSON_CONTAINS(CAST(`config_value` AS JSON), '".out"', '$')
    THEN `config_value`
    ELSE CAST(JSON_MERGE_PRESERVE(
        CAST(`config_value` AS JSON),
        JSON_ARRAY('.in', '.out')
    ) AS CHAR)
END,
    `updated_at` = CURRENT_TIMESTAMP(6)
WHERE `config_key` = 'STORAGE_UPLOAD_ALLOWED_EXTENSIONS';
