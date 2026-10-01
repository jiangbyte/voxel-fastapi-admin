-- migrate_flags_to_int.sql
-- Author: Charlie
-- 将业务标志列 tinyint(1) 改为 INT（0/1）；可按需重复执行。

ALTER TABLE `sys_account_identity` MODIFY COLUMN `verified` int NOT NULL COMMENT '标识是否已完成验证：0 否 / 1 是';
ALTER TABLE `sys_account_identity` MODIFY COLUMN `is_primary` int NOT NULL COMMENT '是否主登录标识：0 次标识 / 1 主标识';
ALTER TABLE `sys_resource` MODIFY COLUMN `is_visible` int NOT NULL COMMENT '是否可见：0 隐藏 / 1 可见';
ALTER TABLE `sys_resource` MODIFY COLUMN `is_cache` int NOT NULL COMMENT '是否缓存路由：0 不缓存 / 1 缓存';
ALTER TABLE `sys_resource` MODIFY COLUMN `is_affix` int NOT NULL COMMENT '是否固定标签页：0 不固定 / 1 固定';
ALTER TABLE `sys_codegen_field` MODIFY COLUMN `in_table` int NOT NULL COMMENT '是否在表格列展示：0 否 / 1 是';
ALTER TABLE `sys_codegen_field` MODIFY COLUMN `in_form` int NOT NULL COMMENT '是否在表单展示：0 否 / 1 是';
ALTER TABLE `sys_codegen_field` MODIFY COLUMN `in_detail` int NOT NULL COMMENT '是否在详情展示：0 否 / 1 是';
ALTER TABLE `sys_codegen_field` MODIFY COLUMN `in_query` int NOT NULL COMMENT '是否作为查询条件：0 否 / 1 是';
ALTER TABLE `sys_codegen_field` MODIFY COLUMN `primary_key` int NOT NULL COMMENT '是否主键列：0 否 / 1 是';
ALTER TABLE `sys_codegen_field` MODIFY COLUMN `required` int NOT NULL COMMENT '是否必填：0 否 / 1 是';
ALTER TABLE `sys_codegen_field` MODIFY COLUMN `unique_flag` int NOT NULL COMMENT '是否唯一：0 否 / 1 是';
ALTER TABLE `sys_codegen_field` MODIFY COLUMN `nullable` int NOT NULL COMMENT '是否允许为空：0 非空 / 1 可空';
ALTER TABLE `sys_config` MODIFY COLUMN `is_builtin` int NOT NULL COMMENT '是否内置配置：0 可维护 / 1 内置不可删';
ALTER TABLE `sys_dept` MODIFY COLUMN `is_virtual` int NOT NULL COMMENT '是否虚拟组织：0 实体 / 1 虚拟';
ALTER TABLE `sys_iam_relation` MODIFY COLUMN `is_primary` int NOT NULL COMMENT '是否主关系/主岗位：0 否 / 1 是';
ALTER TABLE `sys_job` MODIFY COLUMN `enabled` int NOT NULL COMMENT '是否启用调度：0 停用 / 1 启用';
ALTER TABLE `sys_job_log` MODIFY COLUMN `success` int NOT NULL COMMENT '执行结果：0 失败 / 1 成功';
ALTER TABLE `sys_notice` MODIFY COLUMN `is_pinned` int NOT NULL COMMENT '是否置顶（公告）：0 否 / 1 是';
ALTER TABLE `sys_operation_audit_log` MODIFY COLUMN `success` int NOT NULL COMMENT '是否成功：0 失败 / 1 成功';
ALTER TABLE `sys_position` MODIFY COLUMN `is_virtual` int NOT NULL COMMENT '是否虚拟组织：0 实体 / 1 虚拟';
ALTER TABLE `sys_client_resource` MODIFY COLUMN `is_visible` int NOT NULL COMMENT '是否可见：0 隐藏 / 1 可见';
ALTER TABLE `sys_client_resource` MODIFY COLUMN `is_cache` int NOT NULL COMMENT '是否缓存路由：0 不缓存 / 1 缓存';
ALTER TABLE `sys_client_resource` MODIFY COLUMN `is_affix` int NOT NULL COMMENT '是否固定标签页：0 不固定 / 1 固定';
ALTER TABLE `sys_role` MODIFY COLUMN `is_builtin` int NOT NULL COMMENT '是否内置角色：0 自定义 / 1 内置';

-- sys_config：废除 value_type BOOL，改为 NUMBER 0/1
UPDATE `sys_config` SET `value_type` = 'NUMBER', `config_value` = CASE WHEN UPPER(TRIM(`config_value`)) IN ('TRUE','1','YES','Y','ON') THEN '1' ELSE '0' END WHERE UPPER(`value_type`) = 'BOOL';
