import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NotFoundPage from '@/views/404Page.vue'
import DashBoardPage from '@/views/DashBoardPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import SimpleLayout from '@/layouts/SimpleLayout.vue'
import UserInfo from '@/views/UserInfo.vue'
import AppointmentsManagement from '@/views/AppointmentsManagement.vue'
import RecordsManagement from '@/views/RecordsManagement.vue'
import PharmacyManagement from '@/views/PharmacyManagement.vue'
//import InpatientManagement from '@/views/InpatientManagement.vue'
import ReportsManagement from '@/views/ReportsManagement.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashBoardPage,
      meta: {
        requiresAuth: true,
        title: '数据看板',
        sidebar: [
          {
            key: 'sub_overview',
            label: '总览',
            children: [
              { key: 'overview_today', label: '今日概览' },
              { key: 'overview_department', label: '科室概览' },
              { key: 'overview_doctor', label: '医生概览' },
              { key: 'overview_patient', label: '患者概览' },
            ]
          },
          {
            key: 'sub_kpi',
            label: '关键指标',
            children: [
              { key: 'kpi_appointments', label: '预约KPI' },
              { key: 'kpi_revenue', label: '收入KPI' },
              { key: 'kpi_pharmacy', label: '药品使用KPI' },
            ]
          },
          {
            key: 'sub_trends',
            label: '趋势分析',
            children: [
              { key: 'trend_visits', label: '就诊趋势' },
              { key: 'trend_revenue', label: '收入趋势' },
              { key: 'trend_drugs', label: '药品消耗趋势' },
              { key: 'trend_patients', label: '患者分布趋势' },
            ]
          },
        ],
      },
    },
    {
      path: '/appointments',
      name: 'appointments',
      component: AppointmentsManagement,
      meta: {
        requiresAuth: true,
        title: '预约管理',
        sidebar: [
          {
            key: 'sub_list',
            label: '预约列表',
            children: [
              { key: 'list_all', label: '全部预约' },
              { key: 'list_pending', label: '待就诊' },
              { key: 'list_completed', label: '已完成' },
              { key: 'list_cancelled', label: '已取消' },
            ],
          },
          {
            key: 'sub_create',
            label: '新建预约',
            navKey: 'create',
            children: [],
          },
          {
            key: 'sub_schedules',
            label: '医生排班',
            children: [
              { key: 'schedules_roster', label: '医生班表' },
            ],
          },
        ],
      },
    },
    {
      path: '/records',
      name: 'records',
      component: RecordsManagement,
      meta: {
        requiresAuth: true,
        title: '记录管理',
        sidebar: [
          {
            key: 'sub_list',
            label: '病历列表',
            children: [
              { key: 'list_all', label: '全部病历' },
              { key: 'list_by_patient', label: '按患者筛选' },
              { key: 'list_by_doctor', label: '按医生筛选' },
              { key: 'list_by_date', label: '按日期筛选' },
              { key: 'list_by_status', label: '按状态筛选' },
            ]
          },
          {
            key: 'sub_create',
            label: '新建病历',
            navKey: 'create',
            children: []
          },
          {
            key: 'sub_templates',
            label: '模板管理',
            children: [
              { key: 'templates_list', label: '模板列表' },
              { key: 'templates_create', label: '新建模板' },
            ]
          },
        ],
      },
    },
    {
      path: '/pharmacy',
      name: 'pharmacy',
      component: PharmacyManagement,
      meta: {
        requiresAuth: true,
        title: '药房管理',
        sidebar: [
          {
            key: 'sub_inventory',
            label: '库存',
            children: [
              { key: 'inventory_drugs', label: '药品列表' },
              { key: 'inventory_batches', label: '库存批次' },
              { key: 'inventory_low_stock', label: '低库存预警' },
              { key: 'inventory_expiry', label: '效期预警' },
              { key: 'inventory_inout', label: '入库/出库' },
            ]
          },
          {
            key: 'sub_prescriptions',
            label: '处方',
            children: [
              { key: 'prescriptions_list', label: '处方列表' },
              { key: 'prescriptions_pending', label: '待审核' },
              { key: 'prescriptions_approved', label: '已审核' },
              { key: 'prescriptions_dispensed', label: '已发药' },
            ]
          },
          {
            key: 'sub_suppliers',
            label: '供应商',
            children: [
              { key: 'suppliers_list', label: '供应商列表' },
              { key: 'suppliers_create', label: '新建供应商' },
              { key: 'suppliers_orders', label: '采购订单' },
            ]
          },
        ],
      },
    },
    //{
    //  path: '/inpatient',
    //  name: 'inpatient',
    //  component: InpatientManagement,
    //  meta: {
    //    requiresAuth: true,
    //    title: '住院管理',
    //    sidebar: [
    //      {
    //        key: 'sub_wards',
    //        label: '病房',
    //        children: [
    //          { key: 'wards_list', label: '病房列表' },
    //          { key: 'wards_beds', label: '床位管理' },
    //          { key: 'wards_areas', label: '病区设置' },
    //        ]
    //      },
    //      {
    //        key: 'sub_admissions',
    //        label: '入院记录',
    //        children: [
    //          { key: 'admissions_register', label: '住院登记' },
    //          { key: 'admissions_care', label: '护理记录' },
    //          { key: 'admissions_orders', label: '医嘱执行' },
    //          { key: 'admissions_transfer', label: '转科/转床' },
    //        ]
    //      },
    //      {
    //        key: 'sub_discharges',
    //        label: '出院办理',
    //        children: [
    //          { key: 'discharges_process', label: '出院办理' },
    //          { key: 'discharges_settlement', label: '费用结算' },
    //          { key: 'discharges_summary', label: '出院小结' },
    //        ]
    //      },
    //    ],
    //  },
    //},
    //{
    //  path: '/payments',
    //  name: 'payments',
    //  component: PaymentsManagement,
    //  meta: {
    //    requiresAuth: true,
    //    title: '支付管理',
    //    sidebar: [
    //      {
    //        key: 'sub_transactions',
    //        label: '交易记录',
    //        children: [
    //          { key: 'transactions_list', label: '订单列表' },
    //          { key: 'transactions_by_status', label: '按状态' },
    //          { key: 'transactions_abnormal', label: '异常订单' },
    //          { key: 'transactions_export', label: '导出CSV' },
    //        ]
    //      },
    //      {
    //        key: 'sub_refunds',
    //        label: '退款处理',
    //        children: [
    //          { key: 'refunds_apply', label: '退款申请' },
    //          { key: 'refunds_review', label: '退款审核' },
    //          { key: 'refunds_records', label: '退款记录' },
    //        ]
    //      },
    //      {
    //        key: 'sub_methods',
    //        label: '支付方式',
    //        children: [
    //          { key: 'methods_settings', label: '支付方式设置' },
    //          { key: 'methods_channels', label: '渠道配置' },
    //          { key: 'methods_sandbox', label: '沙箱参数' },
    //          { key: 'methods_signature', label: '签名校验' },
    //        ]
    //      },
    //    ],
    //  },
    //},
    {
      path: '/reports',
      name: 'reports',
      component: ReportsManagement,
      meta: {
        requiresAuth: true,
        title: '报告管理',
        sidebar: [
          {
            key: 'sub_daily',
            label: '日报',
            children: [
              { key: 'daily_visits', label: '就诊日报' },
              { key: 'daily_drugs', label: '药品使用日报' },
              { key: 'daily_export', label: '导出CSV' },
            ]
          },
          {
            key: 'sub_monthly',
            label: '月报',
            children: [
              { key: 'monthly_visits', label: '就诊月报' },
              { key: 'monthly_drugs', label: '药品使用月报' },
              { key: 'monthly_compare', label: '趋势对比' },
            ]
          },
          {
            key: 'sub_custom',
            label: '自定义报表',
            children: [
              { key: 'custom_filters', label: '筛选条件' },
              { key: 'custom_fields', label: '字段选择' },
              { key: 'custom_save', label: '保存模板' },
            ]
          },
        ],
      },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { layout: 'blank', guestOnly: true, title: '登录' },
    },
    {
      path: '/register',
      name: 'register',
      component: LoginPage,
      meta: { layout: 'blank', guestOnly: true, title: '注册' },
    },
    {
      path: '/user',
      name: 'user',
      component: UserInfo,
      meta: { layout: SimpleLayout, requiresAuth: true, title: '个人中心' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundPage,
      meta: { layout: SimpleLayout, title: '404' },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (to.meta?.requiresAuth) {
    const ok = await auth.validate()
    if (!ok) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
  }

  if (to.meta?.guestOnly && auth.isAuthenticated) {
    next({ path: '/' })
    return
  }

  const requiredRoles = to.meta?.roles
  if (requiredRoles && (!auth.role || !requiredRoles.includes(auth.role))) {
    next({ path: '/' })
    return
  }

  next()
})

export default router
