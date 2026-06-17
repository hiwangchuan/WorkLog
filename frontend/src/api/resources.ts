import { apiDelete, apiGet, apiPatch, apiPost, apiPut, http, type PageData } from "@/api/http";

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  start_date?: string;
  end_date?: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  project_id?: number;
  due_date?: string;
  estimated_hours: number;
  actual_hours: number;
  created_at: string;
}

export interface WorkLog {
  id: number;
  work_date: string;
  title: string;
  content?: string;
  work_type: string;
  project_id?: number;
  task_id?: number;
  start_time?: string;
  end_time?: string;
  duration_hours: number;
  result?: string;
  problem?: string;
  next_plan?: string;
  visibility: string;
}

export interface Attachment {
  id: number;
  related_type: string;
  related_id: number;
  file_name: string;
  file_url: string;
  mime_type?: string;
  file_size: number;
  summary?: string;
  created_at: string;
}

export interface Team {
  id: number;
  name: string;
  description?: string;
  status: string;
  owner_id: number;
  role?: string;
  member_count: number;
  created_at: string;
}

export interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  username: string;
  email?: string;
  nickname?: string;
  role: string;
  joined_at: string;
}

export interface OvertimeLog {
  id: number;
  overtime_date: string;
  overtime_type: string;
  start_time?: string;
  end_time?: string;
  duration_hours: number;
  reason?: string;
  content?: string;
  approval_status: string;
}

export interface PromptTemplate {
  id: number;
  name: string;
  code: string;
  category: string;
  description?: string;
  system_prompt: string;
  user_prompt: string;
  output_format: string;
  work_domain: string;
  is_default: boolean;
}

export interface ModelConfig {
  id: number;
  provider: string;
  name: string;
  base_url?: string;
  api_key_masked?: string;
  model_name: string;
  temperature: number;
  max_tokens: number;
  timeout_seconds: number;
  is_default: boolean;
}

export interface GenerationRecord {
  id: number;
  report_type: string;
  date_start: string;
  date_end: string;
  input_snapshot: Record<string, unknown>;
  prompt_content: string;
  ai_output?: string;
  final_output?: string;
  status: string;
  error_message?: string;
  created_at: string;
}

export const dashboardApi = {
  summary: () => apiGet<any>("/dashboard/summary"),
  workTrend: () => apiGet<any[]>("/dashboard/work-hours-trend"),
  taskStatus: () => apiGet<any[]>("/dashboard/task-status"),
  projectHours: () => apiGet<any[]>("/dashboard/project-hours"),
  overtimeTrend: () => apiGet<any[]>("/dashboard/overtime-trend")
};

export const projectApi = {
  list: (params?: Record<string, unknown>) => apiGet<PageData<Project>>("/projects", params),
  create: (data: Partial<Project>) => apiPost<Project>("/projects", data),
  update: (id: number, data: Partial<Project>) => apiPut<Project>(`/projects/${id}`, data),
  remove: (id: number) => apiDelete(`/projects/${id}`)
};

export const taskApi = {
  list: (params?: Record<string, unknown>) => apiGet<PageData<Task>>("/tasks", params),
  create: (data: Partial<Task>) => apiPost<Task>("/tasks", data),
  update: (id: number, data: Partial<Task>) => apiPut<Task>(`/tasks/${id}`, data),
  status: (id: number, status: string) => apiPatch<Task>(`/tasks/${id}/status`, { status }),
  remove: (id: number) => apiDelete(`/tasks/${id}`)
};

export const workLogApi = {
  list: (params?: Record<string, unknown>) => apiGet<PageData<WorkLog>>("/work-logs", params),
  create: (data: Partial<WorkLog>) => apiPost<WorkLog>("/work-logs", data),
  update: (id: number, data: Partial<WorkLog>) => apiPut<WorkLog>(`/work-logs/${id}`, data),
  remove: (id: number) => apiDelete(`/work-logs/${id}`)
};

export const attachmentApi = {
  list: (relatedType: string, relatedId: number) => apiGet<Attachment[]>("/attachments", { related_type: relatedType, related_id: relatedId }),
  upload: (relatedType: string, relatedId: number, file: File, summary?: string) => {
    const form = new FormData();
    form.append("related_type", relatedType);
    form.append("related_id", String(relatedId));
    if (summary) form.append("summary", summary);
    form.append("file", file);
    return apiPost<Attachment>("/attachments", form);
  },
  update: (id: number, data: Partial<Attachment>) => apiPut<Attachment>(`/attachments/${id}`, data),
  remove: (id: number) => apiDelete(`/attachments/${id}`),
  downloadUrl: (id: number) => `/api/attachments/${id}/download`
};

export const overtimeApi = {
  list: (params?: Record<string, unknown>) => apiGet<PageData<OvertimeLog>>("/overtime-logs", params),
  create: (data: Partial<OvertimeLog>) => apiPost<OvertimeLog>("/overtime-logs", data),
  update: (id: number, data: Partial<OvertimeLog>) => apiPut<OvertimeLog>(`/overtime-logs/${id}`, data),
  submit: (id: number) => apiPost(`/overtime-logs/${id}/submit`),
  remove: (id: number) => apiDelete(`/overtime-logs/${id}`)
};

export const aiApi = {
  models: () => apiGet<ModelConfig[]>("/ai/model-configs"),
  createModel: (data: Partial<ModelConfig> & { api_key?: string }) => apiPost<ModelConfig>("/ai/model-configs", data),
  updateModel: (id: number, data: Partial<ModelConfig> & { api_key?: string }) => apiPut<ModelConfig>(`/ai/model-configs/${id}`, data),
  deleteModel: (id: number) => apiDelete(`/ai/model-configs/${id}`),
  testModel: (id: number) => apiPost(`/ai/model-configs/${id}/test`),
  templates: () => apiGet<PromptTemplate[]>("/ai/prompt-templates"),
  createTemplate: (data: Partial<PromptTemplate>) => apiPost<PromptTemplate>("/ai/prompt-templates", data),
  updateTemplate: (id: number, data: Partial<PromptTemplate>) => apiPut<PromptTemplate>(`/ai/prompt-templates/${id}`, data),
  deleteTemplate: (id: number) => apiDelete(`/ai/prompt-templates/${id}`),
  generateWeekly: (data: Record<string, unknown>) => apiPost<GenerationRecord>("/ai/reports/weekly/generate", data),
  records: (params?: Record<string, unknown>) => apiGet<PageData<GenerationRecord>>("/ai/generation-records", params),
  updateFinal: (id: number, final_output: string) => apiPut<GenerationRecord>(`/ai/generation-records/${id}/final-output`, { final_output }),
  deleteRecord: (id: number) => apiDelete(`/ai/generation-records/${id}`),
  previewDesensitize: (text: string) => apiPost<{ before: string; after: string }>("/ai/desensitize/preview", { text })
};

export const statisticsApi = {
  tasks: () => apiGet<any>("/statistics/tasks"),
  workHours: () => apiGet<any>("/statistics/work-hours"),
  overtime: () => apiGet<any>("/statistics/overtime"),
  projects: () => apiGet<any[]>("/statistics/projects"),
  workTypes: () => apiGet<any[]>("/statistics/work-types"),
  heatmap: () => apiGet<any[]>("/statistics/calendar-heatmap")
};

export const teamApi = {
  list: (params?: Record<string, unknown>) => apiGet<PageData<Team>>("/teams", params),
  create: (data: Partial<Team>) => apiPost<Team>("/teams", data),
  update: (id: number, data: Partial<Team>) => apiPut<Team>(`/teams/${id}`, data),
  remove: (id: number) => apiDelete(`/teams/${id}`),
  members: (id: number) => apiGet<TeamMember[]>(`/teams/${id}/members`),
  addMember: (id: number, data: { username: string; role: string }) => apiPost<TeamMember>(`/teams/${id}/members`, data),
  updateMember: (teamId: number, memberId: number, role: string) => apiPut(`/teams/${teamId}/members/${memberId}`, { role }),
  removeMember: (teamId: number, memberId: number) => apiDelete(`/teams/${teamId}/members/${memberId}`)
};

export function exportUrl(recordId: number, format = "markdown") {
  return `/api/reports/export?record_id=${recordId}&format=${format}`;
}

export async function downloadExport(recordId: number, format: string) {
  const response = await http.get(`/reports/export?record_id=${recordId}&format=${format}`, { responseType: "blob" });
  const url = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = `worklog-report.${format === "excel" ? "xlsx" : format === "word" ? "docx" : format}`;
  link.click();
  URL.revokeObjectURL(url);
}
