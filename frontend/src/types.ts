export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type AgentTaskCreated = {
  task_id: string;
  status: string;
  message: string;
};

export type TaskType = 'payment_investigation' | 'reconciliation' | 'financial_research';

export type ApiResult = Record<string, unknown>;
