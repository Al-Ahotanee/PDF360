export type PDFFile = {
  id: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  is_favorite: boolean;
  created_at: string;
};

export type Job = {
  id: string;
  job_type: string;
  status: "queued" | "processing" | "done" | "failed";
  result: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
};

export type DashboardStats = {
  storage_used_bytes: number;
  file_count: number;
  jobs_last_30_days: number;
};

export type Subscription = {
  id: string;
  plan: "free" | "premium_monthly" | "premium_yearly";
  status: "active" | "canceled" | "past_due" | "expired";
  current_period_end: string | null;
  created_at: string;
};

export type Payment = {
  id: string;
  amount: number;
  currency: string;
  status: "pending" | "succeeded" | "failed" | "refunded";
  created_at: string;
};

export type ApiKey = {
  id: string;
  name: string;
  key_prefix: string;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
};

export type ApiKeyCreated = ApiKey & { raw_key: string };

export type SharePermission = "view" | "comment" | "edit";

export type FileShare = {
  id: string;
  file_id: string;
  owner_id: string;
  shared_with_id: string;
  permission: SharePermission;
  created_at: string;
  shared_with_email: string | null;
};

export type SharedWithMe = {
  id: string;
  file_id: string;
  original_filename: string;
  mime_type: string;
  size_bytes: number;
  permission: SharePermission;
  owner_email: string | null;
  created_at: string;
};

export type ActivityLogEntry = {
  id: string;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
};

export type FeatureFlag = {
  key: string;
  value: Record<string, unknown>;
  description: string | null;
  created_at: string;
  updated_at: string;
};
