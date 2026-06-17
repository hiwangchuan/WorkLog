export const taskStatusOptions = [
  { label: "待开始", value: "todo", type: "default" },
  { label: "进行中", value: "in_progress", type: "info" },
  { label: "阻塞", value: "blocked", type: "warning" },
  { label: "已完成", value: "completed", type: "success" },
  { label: "已取消", value: "cancelled", type: "default" }
];

export const priorityOptions = [
  { label: "低", value: "low", type: "default" },
  { label: "中", value: "medium", type: "info" },
  { label: "高", value: "high", type: "warning" },
  { label: "紧急", value: "urgent", type: "error" }
];

export const workTypeOptions = [
  { label: "日常工作", value: "daily" },
  { label: "项目工作", value: "project" },
  { label: "会议", value: "meeting" },
  { label: "运维", value: "operation" },
  { label: "安全分析", value: "security" },
  { label: "故障/应急", value: "incident" },
  { label: "文档", value: "document" },
  { label: "开发", value: "development" },
  { label: "测试", value: "testing" },
  { label: "学习", value: "learning" },
  { label: "其他", value: "other" }
];

export const overtimeTypeOptions = [
  { label: "工作日加班", value: "weekday" },
  { label: "周末加班", value: "weekend" },
  { label: "节假日加班", value: "holiday" },
  { label: "夜间值班", value: "night_shift" }
];

export const securityTemplates = [
  "WAF/API 设备巡检",
  "WAF 告警分析",
  "蜜罐告警分析",
  "态势工单处理",
  "站点接入支撑",
  "端口分配",
  "网络连通性测试",
  "策略调整",
  "证书替换",
  "重保值守",
  "攻防演练支撑",
  "周报整理",
  "会议沟通",
  "故障排查",
  "应急响应"
];

export function labelOf(options: { label: string; value: string }[], value: string) {
  return options.find((item) => item.value === value)?.label || value;
}

export function tagType(options: { value: string; type?: string }[], value: string) {
  return options.find((item) => item.value === value)?.type || "default";
}
