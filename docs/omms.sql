/*
 Navicat Premium Data Transfer

 Source Server         : ayanami
 Source Server Type    : MySQL
 Source Server Version : 50736
 Source Host           : localhost:3306
 Source Schema         : medical_system

 Target Server Type    : MySQL
 Target Server Version : 50736
 File Encoding         : 65001

 Date: 01/12/2025 10:38:11
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for appointments
-- ----------------------------
DROP TABLE IF EXISTS `appointments`;
CREATE TABLE `appointments`  (
  `appt_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '预约ID',
  `patient_id` bigint(20) NOT NULL COMMENT '患者ID',
  `doctor_id` bigint(20) NOT NULL COMMENT '医生ID',
  `appt_time` datetime NOT NULL COMMENT '预约时间',
  `status` tinyint(4) NULL DEFAULT 0 COMMENT '状态：0-待就诊，1-已就诊，2-已取消，3-已完成',
  `symptom_desc` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '症状描述',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`appt_id`) USING BTREE,
  UNIQUE INDEX `uk_doctor_time`(`doctor_id`, `appt_time`) USING BTREE,
  INDEX `idx_appointments_patient_id`(`patient_id`) USING BTREE,
  INDEX `idx_appointments_doctor_id`(`doctor_id`) USING BTREE,
  INDEX `idx_appointments_appt_time`(`appt_time`) USING BTREE,
  INDEX `idx_appointments_status`(`status`) USING BTREE,
  CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '预约表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of appointments
-- ----------------------------

-- ----------------------------
-- Table structure for departments
-- ----------------------------
DROP TABLE IF EXISTS `departments`;
CREATE TABLE `departments`  (
  `dept_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '科室ID',
  `dept_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '科室名称',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '科室描述',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`dept_id`) USING BTREE,
  UNIQUE INDEX `dept_name`(`dept_name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '科室表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of departments
-- ----------------------------
INSERT INTO `departments` VALUES (1, '内科', '内科科室', '2025-11-14 11:13:59', '2025-11-14 11:13:59');
INSERT INTO `departments` VALUES (2, '外科', '外科科室', '2025-11-14 11:13:59', '2025-11-14 11:13:59');
INSERT INTO `departments` VALUES (3, '儿科', '儿科科室', '2025-11-14 11:13:59', '2025-11-14 11:13:59');
INSERT INTO `departments` VALUES (4, '妇产科', '妇产科科室', '2025-11-14 11:13:59', '2025-11-14 11:13:59');
INSERT INTO `departments` VALUES (5, '眼科', '眼科科室', '2025-11-14 11:13:59', '2025-11-14 11:13:59');
INSERT INTO `departments` VALUES (6, '耳鼻喉科', '耳鼻喉科科室', '2025-11-14 11:13:59', '2025-11-14 11:13:59');
INSERT INTO `departments` VALUES (7, '口腔科', '口腔科科室', '2025-11-14 11:13:59', '2025-11-14 11:13:59');
INSERT INTO `departments` VALUES (8, '皮肤科', '皮肤科科室', '2025-11-14 11:13:59', '2025-11-14 11:13:59');

-- ----------------------------
-- Table structure for doctor_schedules
-- ----------------------------
DROP TABLE IF EXISTS `doctor_schedules`;
CREATE TABLE `doctor_schedules`  (
  `schedule_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '排班ID',
  `doctor_id` bigint(20) NOT NULL COMMENT '医生ID',
  `work_date` date NOT NULL COMMENT '工作日期',
  `start_time` time NOT NULL COMMENT '上班时间',
  `end_time` time NOT NULL COMMENT '下班时间',
  `max_appointments` int(11) NULL DEFAULT 20 COMMENT '最大预约数',
  `status` tinyint(4) NULL DEFAULT 1 COMMENT '状态：0-休息，1-出诊',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`schedule_id`) USING BTREE,
  UNIQUE INDEX `uk_doctor_date`(`doctor_id`, `work_date`) USING BTREE,
  CONSTRAINT `doctor_schedules_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '医生排班表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of doctor_schedules
-- ----------------------------

-- ----------------------------
-- Table structure for doctors
-- ----------------------------
DROP TABLE IF EXISTS `doctors`;
CREATE TABLE `doctors`  (
  `doctor_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '医生ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '医生姓名',
  `department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '所属科室',
  `title` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '职称',
  `specialty` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '专长',
  `intro` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '医生简介',
  `available_status` tinyint(4) NULL DEFAULT 1 COMMENT '出诊状态：0-不出诊，1-出诊',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`doctor_id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `idx_doctors_department`(`department`) USING BTREE,
  INDEX `idx_doctors_available_status`(`available_status`) USING BTREE,
  CONSTRAINT `doctors_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '医生表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of doctors
-- ----------------------------

-- ----------------------------
-- Table structure for fee_bills
-- ----------------------------
DROP TABLE IF EXISTS `fee_bills`;
CREATE TABLE `fee_bills`  (
  `bill_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '账单ID',
  `patient_id` bigint(20) NOT NULL COMMENT '患者ID',
  `bill_type` tinyint(4) NOT NULL COMMENT '账单类型：0-门诊，1-住院',
  `total_amount` decimal(10, 2) NOT NULL COMMENT '总金额',
  `paid_amount` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '已支付金额',
  `status` tinyint(4) NULL DEFAULT 0 COMMENT '状态：0-未支付，1-已支付，2-已取消',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `paid_time` datetime NULL DEFAULT NULL COMMENT '支付时间',
  PRIMARY KEY (`bill_id`) USING BTREE,
  INDEX `patient_id`(`patient_id`) USING BTREE,
  CONSTRAINT `fee_bills_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '费用清单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of fee_bills
-- ----------------------------

-- ----------------------------
-- Table structure for hospital_records
-- ----------------------------
DROP TABLE IF EXISTS `hospital_records`;
CREATE TABLE `hospital_records`  (
  `hosp_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '住院记录ID',
  `patient_id` bigint(20) NOT NULL COMMENT '患者ID',
  `room_id` bigint(20) NOT NULL COMMENT '病房ID',
  `admit_time` datetime NOT NULL COMMENT '入院时间',
  `discharge_time` datetime NULL DEFAULT NULL COMMENT '出院时间',
  `admit_diagnosis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '入院诊断',
  `discharge_diagnosis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '出院诊断',
  `status` tinyint(4) NULL DEFAULT 0 COMMENT '状态：0-住院中，1-已出院',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`hosp_id`) USING BTREE,
  INDEX `patient_id`(`patient_id`) USING BTREE,
  CONSTRAINT `hospital_records_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '住院记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of hospital_records
-- ----------------------------

-- ----------------------------
-- Table structure for inspection_applications
-- ----------------------------
DROP TABLE IF EXISTS `inspection_applications`;
CREATE TABLE `inspection_applications`  (
  `appl_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '申请ID',
  `patient_id` bigint(20) NOT NULL COMMENT '患者ID',
  `doctor_id` bigint(20) NOT NULL COMMENT '医生ID',
  `inspection_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '检查类型',
  `inspection_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '检查项目名称',
  `apply_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
  `scheduled_time` datetime NULL DEFAULT NULL COMMENT '预约检查时间',
  `status` tinyint(4) NULL DEFAULT 0 COMMENT '状态：0-待检查，1-检查中，2-已完成',
  `result_id` bigint(20) NULL DEFAULT NULL COMMENT '检查结果ID',
  PRIMARY KEY (`appl_id`) USING BTREE,
  INDEX `patient_id`(`patient_id`) USING BTREE,
  INDEX `doctor_id`(`doctor_id`) USING BTREE,
  CONSTRAINT `inspection_applications_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `inspection_applications_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '检查申请表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of inspection_applications
-- ----------------------------

-- ----------------------------
-- Table structure for inspection_results
-- ----------------------------
DROP TABLE IF EXISTS `inspection_results`;
CREATE TABLE `inspection_results`  (
  `result_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '结果ID',
  `appl_id` bigint(20) NOT NULL COMMENT '申请ID',
  `result_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '检查结果数据',
  `conclusion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '结论',
  `report_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '报告文件URL',
  `doctor_id` bigint(20) NOT NULL COMMENT '医生ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`result_id`) USING BTREE,
  UNIQUE INDEX `appl_id`(`appl_id`) USING BTREE,
  INDEX `doctor_id`(`doctor_id`) USING BTREE,
  CONSTRAINT `inspection_results_ibfk_1` FOREIGN KEY (`appl_id`) REFERENCES `inspection_applications` (`appl_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `inspection_results_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '检查结果表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of inspection_results
-- ----------------------------

-- ----------------------------
-- Table structure for medical_record_versions
-- ----------------------------
DROP TABLE IF EXISTS `medical_record_versions`;
CREATE TABLE `medical_record_versions`  (
  `version_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '版本ID',
  `record_id` bigint(20) NOT NULL COMMENT '病历ID',
  `version_number` int(11) NOT NULL COMMENT '版本号',
  `diagnosis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '诊断结果',
  `treatment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '治疗方案',
  `updated_by` bigint(20) NOT NULL COMMENT '更新人ID',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`version_id`) USING BTREE,
  INDEX `record_id`(`record_id`) USING BTREE,
  INDEX `updated_by`(`updated_by`) USING BTREE,
  CONSTRAINT `medical_record_versions_ibfk_1` FOREIGN KEY (`record_id`) REFERENCES `medical_records` (`record_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `medical_record_versions_ibfk_2` FOREIGN KEY (`updated_by`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '病历版本表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of medical_record_versions
-- ----------------------------

-- ----------------------------
-- Table structure for medical_records
-- ----------------------------
DROP TABLE IF EXISTS `medical_records`;
CREATE TABLE `medical_records`  (
  `record_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '病历ID',
  `patient_id` bigint(20) NOT NULL COMMENT '患者ID',
  `doctor_id` bigint(20) NOT NULL COMMENT '医生ID',
  `visit_date` datetime NOT NULL COMMENT '就诊日期',
  `diagnosis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '诊断结果',
  `treatment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '治疗方案',
  `prescription_id` bigint(20) NULL DEFAULT NULL COMMENT '处方ID',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `idx_medical_records_patient_id`(`patient_id`) USING BTREE,
  INDEX `idx_medical_records_doctor_id`(`doctor_id`) USING BTREE,
  INDEX `idx_medical_records_visit_date`(`visit_date`) USING BTREE,
  CONSTRAINT `medical_records_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `medical_records_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '病历表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of medical_records
-- ----------------------------

-- ----------------------------
-- Table structure for medicine_stocks
-- ----------------------------
DROP TABLE IF EXISTS `medicine_stocks`;
CREATE TABLE `medicine_stocks`  (
  `stock_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '库存ID',
  `medicine_id` bigint(20) NOT NULL COMMENT '药品ID',
  `current_stock` int(11) NULL DEFAULT 0 COMMENT '当前库存',
  `last_stock_in_time` datetime NULL DEFAULT NULL COMMENT '最后入库时间',
  `last_stock_out_time` datetime NULL DEFAULT NULL COMMENT '最后出库时间',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`stock_id`) USING BTREE,
  UNIQUE INDEX `medicine_id`(`medicine_id`) USING BTREE,
  INDEX `idx_medicine_stocks_medicine_id`(`medicine_id`) USING BTREE,
  INDEX `idx_medicine_stocks_current_stock`(`current_stock`) USING BTREE,
  CONSTRAINT `medicine_stocks_ibfk_1` FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`medicine_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '药品库存表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of medicine_stocks
-- ----------------------------

-- ----------------------------
-- Table structure for medicines
-- ----------------------------
DROP TABLE IF EXISTS `medicines`;
CREATE TABLE `medicines`  (
  `medicine_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '药品ID',
  `medicine_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '药品名称',
  `specification` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '规格',
  `dosage_form` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '剂型',
  `manufacturer` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '生产厂家',
  `unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '单位',
  `price` decimal(10, 2) NOT NULL COMMENT '单价',
  `warning_stock` int(11) NULL DEFAULT 50 COMMENT '预警库存',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`medicine_id`) USING BTREE,
  INDEX `idx_medicines_name`(`medicine_name`) USING BTREE,
  INDEX `idx_medicines_manufacturer`(`manufacturer`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '药品表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of medicines
-- ----------------------------

-- ----------------------------
-- Table structure for nurses
-- ----------------------------
DROP TABLE IF EXISTS `nurses`;
CREATE TABLE `nurses`  (
  `nurse_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '护士ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '护士姓名',
  `department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '所属科室',
  `title` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '职称',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`nurse_id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `nurses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '护士表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of nurses
-- ----------------------------

-- ----------------------------
-- Table structure for operation_logs
-- ----------------------------
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE `operation_logs`  (
  `log_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `user_id` bigint(20) NOT NULL COMMENT '操作用户ID',
  `user_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '操作用户名',
  `operation_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '操作类型',
  `operation_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '操作内容',
  `ip_address` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户代理',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`log_id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `operation_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '操作日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of operation_logs
-- ----------------------------

-- ----------------------------
-- Table structure for patients
-- ----------------------------
DROP TABLE IF EXISTS `patients`;
CREATE TABLE `patients`  (
  `patient_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '患者ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '患者姓名',
  `gender` tinyint(4) NULL DEFAULT NULL COMMENT '性别：0-女，1-男',
  `birthday` date NULL DEFAULT NULL COMMENT '出生日期',
  `id_card` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '身份证号',
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '地址',
  `emergency_contact` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '紧急联系人',
  `emergency_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '紧急联系电话',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`patient_id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id`) USING BTREE,
  UNIQUE INDEX `id_card`(`id_card`) USING BTREE,
  INDEX `idx_patients_name`(`name`) USING BTREE,
  INDEX `idx_patients_id_card`(`id_card`) USING BTREE,
  CONSTRAINT `patients_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '患者表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of patients
-- ----------------------------

-- ----------------------------
-- Table structure for payment_records
-- ----------------------------
DROP TABLE IF EXISTS `payment_records`;
CREATE TABLE `payment_records`  (
  `payment_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '支付记录ID',
  `bill_id` bigint(20) NOT NULL COMMENT '账单ID',
  `payment_method` tinyint(4) NOT NULL COMMENT '支付方式：0-支付宝，1-微信支付，2-银联',
  `amount` decimal(10, 2) NOT NULL COMMENT '支付金额',
  `transaction_no` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '交易单号',
  `status` tinyint(4) NOT NULL COMMENT '支付状态：0-失败，1-成功',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`payment_id`) USING BTREE,
  UNIQUE INDEX `transaction_no`(`transaction_no`) USING BTREE,
  INDEX `bill_id`(`bill_id`) USING BTREE,
  CONSTRAINT `payment_records_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `fee_bills` (`bill_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '支付记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of payment_records
-- ----------------------------

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions`  (
  `perm_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '权限ID',
  `perm_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '权限名称',
  `perm_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '权限代码',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '权限描述',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`perm_id`) USING BTREE,
  UNIQUE INDEX `perm_name`(`perm_name`) USING BTREE,
  UNIQUE INDEX `perm_code`(`perm_code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '权限表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of permissions
-- ----------------------------
INSERT INTO `permissions` VALUES (1, '用户管理', 'user:manage', '管理系统用户', '2025-11-14 11:09:55', '2025-11-14 11:09:55');
INSERT INTO `permissions` VALUES (2, '角色管理', 'role:manage', '管理系统角色', '2025-11-14 11:09:55', '2025-11-14 11:09:55');
INSERT INTO `permissions` VALUES (3, '权限管理', 'perm:manage', '管理系统权限', '2025-11-14 11:09:55', '2025-11-14 11:09:55');
INSERT INTO `permissions` VALUES (4, '预约管理', 'appointment:manage', '管理预约', '2025-11-14 11:09:55', '2025-11-14 11:09:55');
INSERT INTO `permissions` VALUES (5, '病历管理', 'record:manage', '管理病历', '2025-11-14 11:09:55', '2025-11-14 11:09:55');
INSERT INTO `permissions` VALUES (6, '药品管理', 'medicine:manage', '管理药品', '2025-11-14 11:09:55', '2025-11-14 11:09:55');
INSERT INTO `permissions` VALUES (7, '支付管理', 'payment:manage', '管理支付', '2025-11-14 11:09:55', '2025-11-14 11:09:55');
INSERT INTO `permissions` VALUES (8, '检查管理', 'inspection:manage', '管理检查', '2025-11-14 11:09:55', '2025-11-14 11:09:55');

-- ----------------------------
-- Table structure for prescription_medicines
-- ----------------------------
DROP TABLE IF EXISTS `prescription_medicines`;
CREATE TABLE `prescription_medicines`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `prescription_id` bigint(20) NOT NULL COMMENT '处方ID',
  `medicine_id` bigint(20) NOT NULL COMMENT '药品ID',
  `quantity` int(11) NOT NULL COMMENT '数量',
  `dosage` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用法用量',
  `unit_price` decimal(10, 2) NOT NULL COMMENT '单价',
  `subtotal` decimal(10, 2) NOT NULL COMMENT '小计',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `prescription_id`(`prescription_id`) USING BTREE,
  INDEX `medicine_id`(`medicine_id`) USING BTREE,
  CONSTRAINT `prescription_medicines_ibfk_1` FOREIGN KEY (`prescription_id`) REFERENCES `prescriptions` (`prescription_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `prescription_medicines_ibfk_2` FOREIGN KEY (`medicine_id`) REFERENCES `medicines` (`medicine_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '处方药品表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of prescription_medicines
-- ----------------------------

-- ----------------------------
-- Table structure for prescriptions
-- ----------------------------
DROP TABLE IF EXISTS `prescriptions`;
CREATE TABLE `prescriptions`  (
  `prescription_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '处方ID',
  `patient_id` bigint(20) NOT NULL COMMENT '患者ID',
  `doctor_id` bigint(20) NOT NULL COMMENT '医生ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `status` tinyint(4) NULL DEFAULT 0 COMMENT '状态：0-待审核，1-已审核，2-已发药',
  `total_amount` decimal(10, 2) NULL DEFAULT 0.00 COMMENT '总金额',
  PRIMARY KEY (`prescription_id`) USING BTREE,
  INDEX `patient_id`(`patient_id`) USING BTREE,
  INDEX `doctor_id`(`doctor_id`) USING BTREE,
  CONSTRAINT `prescriptions_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `prescriptions_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '处方表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of prescriptions
-- ----------------------------

-- ----------------------------
-- Table structure for role_permissions
-- ----------------------------
DROP TABLE IF EXISTS `role_permissions`;
CREATE TABLE `role_permissions`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `role_id` bigint(20) NOT NULL COMMENT '角色ID',
  `perm_id` bigint(20) NOT NULL COMMENT '权限ID',
  `created_at` datetime NULL COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_role_perm`(`role_id`, `perm_id`) USING BTREE,
  INDEX `perm_id`(`perm_id`) USING BTREE,
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`perm_id`) REFERENCES `permissions` (`perm_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '角色权限关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of role_permissions
-- ----------------------------
INSERT INTO `role_permissions` VALUES (1, 1, 7, '2025-11-14 11:10:06');
INSERT INTO `role_permissions` VALUES (2, 1, 3, '2025-11-14 11:10:06');
INSERT INTO `role_permissions` VALUES (3, 1, 8, '2025-11-14 11:10:06');
INSERT INTO `role_permissions` VALUES (4, 1, 1, '2025-11-14 11:10:06');
INSERT INTO `role_permissions` VALUES (5, 1, 5, '2025-11-14 11:10:06');
INSERT INTO `role_permissions` VALUES (6, 1, 6, '2025-11-14 11:10:06');
INSERT INTO `role_permissions` VALUES (7, 1, 2, '2025-11-14 11:10:06');
INSERT INTO `role_permissions` VALUES (8, 1, 4, '2025-11-14 11:10:06');
INSERT INTO `role_permissions` VALUES (16, 2, 4, '2025-11-14 11:10:31');
INSERT INTO `role_permissions` VALUES (17, 2, 5, '2025-11-14 11:10:31');

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `role_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `role_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色名称',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '角色描述',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`role_id`) USING BTREE,
  UNIQUE INDEX `role_name`(`role_name`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '角色表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of roles
-- ----------------------------
INSERT INTO `roles` VALUES (1, 'ADMIN', '系统管理员', '2025-11-14 11:09:28', '2025-11-14 11:09:28');
INSERT INTO `roles` VALUES (2, 'DOCTOR', '医生', '2025-11-14 11:09:28', '2025-11-14 11:09:28');
INSERT INTO `roles` VALUES (3, 'PATIENT', '患者', '2025-11-14 11:09:28', '2025-11-14 11:09:28');
INSERT INTO `roles` VALUES (4, 'NURSE', '护士', '2025-11-14 11:09:28', '2025-11-14 11:09:28');
INSERT INTO `roles` VALUES (5, 'PHARMACIST', '药剂师', '2025-11-14 11:09:28', '2025-11-14 11:09:28');

-- ----------------------------
-- Table structure for rooms
-- ----------------------------
DROP TABLE IF EXISTS `rooms`;
CREATE TABLE `rooms`  (
  `room_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '病房ID',
  `room_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '病房号',
  `room_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '病房类型',
  `bed_count` int(11) NULL DEFAULT 1 COMMENT '床位数',
  `available_beds` int(11) NULL DEFAULT 1 COMMENT '可用床位数',
  `price_per_day` decimal(10, 2) NOT NULL COMMENT '每日价格',
  `status` tinyint(4) NULL DEFAULT 1 COMMENT '状态：0-不可用，1-可用',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`room_id`) USING BTREE,
  UNIQUE INDEX `room_number`(`room_number`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '病房表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of rooms
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '密码（加密存储）',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '邮箱',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '手机号',
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `status` tinyint(4) NULL DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
  `created_at` datetime NULL COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login_at` datetime NULL DEFAULT NULL COMMENT '最后登录时间',
  `role_id` bigint(20) NULL DEFAULT NULL COMMENT '角色ID',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE,
  UNIQUE INDEX `email`(`email`) USING BTREE,
  UNIQUE INDEX `phone`(`phone`) USING BTREE,
  INDEX `idx_users_role_id`(`role_id`) USING BTREE,
  INDEX `idx_users_status`(`status`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', '$2a$10$7J7FqQZ8q3r6s5t4u3i2o1p0o1i2u3y4t5r6e7w8q9r0t1y2u3i', 'admin@medical.com', '13800138000', '系统管理员', 1, '2025-11-14 11:13:45', '2025-11-14 11:13:45', NULL, 1);


SET FOREIGN_KEY_CHECKS = 1;
