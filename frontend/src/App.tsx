import { useCallback, useEffect, useMemo, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import {
  Activity, ArrowDownToLine, ArrowRight, ArrowUpRight, Bot, Building2,
  CheckCircle2, ChevronDown, CircleHelp, Clock3, CreditCard, Database,
  FileText, Files, LayoutDashboard, LogOut, Menu, RefreshCw,
  ScanSearch, Send, ShieldCheck, Sparkles, UploadCloud, WalletCards, X,
} from 'lucide-react';
import { apiRequest, clearSession, getAccessToken, getSavedEmail, loginRequest, registerRequest, saveSession } from './lib/api';
import type { AgentTaskCreated, TaskType, TokenResponse } from './types';

type Page = 'overview' | 'agent' | 'imports' | 'documents' | 'reports';

const NAV_ITEMS: { id: Page; label: string; icon: typeof LayoutDashboard; description: string }[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard, description: 'Your financial operations at a glance' },
  { id: 'agent', label: 'Agent workspace', icon: Bot, description: 'Launch AI-powered financial investigations' },
  { id: 'imports', label: 'Data imports', icon: Database, description: 'Load merchant and financial records' },
  { id: 'documents', label: 'Knowledge base', icon: Files, description: 'Upload documents for retrieval and research' },
  { id: 'reports', label: 'Reports', icon: FileText, description: 'Review agent outputs and findings' },
];

const TASK_OPTIONS: { value: TaskType; label: string; detail: string }[] = [
  { value: 'payment_investigation', label: 'Payment investigation', detail: 'Investigate payment performance, failures and unusual patterns.' },
  { value: 'reconciliation', label: 'Reconciliation', detail: 'Investigate settlement and transaction discrepancies.' },
  { value: 'financial_research', label: 'Financial research', detail: 'Research a financial or operational question using available sources.' },
];

function cx(...classes: (string | false | null | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}

function friendlyError(error: unknown) {
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.';
}

function readMerchantId() {
  return localStorage.getItem('finpilot_merchant_id') || '';
}

function saveMerchantId(value: string) {
  localStorage.setItem('finpilot_merchant_id', value.trim());
}

function App() {
  const [token, setToken] = useState<string | null>(getAccessToken());
  const [email, setEmail] = useState(getSavedEmail());
  const [page, setPage] = useState<Page>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [merchantId, setMerchantId] = useState(readMerchantId());
  const [toast, setToast] = useState<{ kind: 'success' | 'error' | 'info'; text: string } | null>(null);

  const notify = useCallback((kind: 'success' | 'error' | 'info', text: string) => {
    setToast({ kind, text });
    window.setTimeout(() => setToast(null), 4800);
  }, []);

  const onAuthenticated = (data: TokenResponse, userEmail: string) => {
    saveSession(data.access_token, userEmail);
    setToken(data.access_token);
    setEmail(userEmail);
    notify('success', 'Welcome to your FinPilot-AI workspace.');
  };

  const signOut = async () => {
    try {
      await apiRequest('/auth/logout', { method: 'POST' }, false);
    } catch {
      // Local sign-out still clears the browser session if the API is unavailable.
    }
    clearSession();
    setToken(null);
    setEmail('');
    notify('info', 'You have been signed out.');
  };

  const updateMerchant = (value: string) => {
    setMerchantId(value);
    saveMerchantId(value);
  };

  if (!token) {
    return <AuthScreen onAuthenticated={onAuthenticated} />;
  }

  const activeNav = NAV_ITEMS.find((item) => item.id === page) || NAV_ITEMS[0];

  return (
    <div className="app-shell">
      <aside className={cx('sidebar', sidebarOpen && 'sidebar-open')}>
        <div className="brand-lockup">
          <div className="brand-mark"><Activity size={21} strokeWidth={2.5} /></div>
          <div>
            <div className="brand-name">FinPilot<span>-AI</span></div>
            <div className="brand-caption">FINANCIAL INTELLIGENCE</div>
          </div>
          <button className="icon-button sidebar-close" onClick={() => setSidebarOpen(false)} aria-label="Close navigation"><X size={18} /></button>
        </div>

        <div className="workspace-switcher">
          <div className="workspace-avatar">FP</div>
          <div className="workspace-copy"><strong>FinPilot workspace</strong><span>Demo environment</span></div>
          <ChevronDown size={15} className="muted-icon" />
        </div>

        <div className="nav-label">WORKSPACE</div>
        <nav className="side-nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id} className={cx('nav-item', page === item.id && 'nav-item-active')} onClick={() => { setPage(item.id); setSidebarOpen(false); }}>
                <Icon size={18} strokeWidth={1.9} />
                <span>{item.label}</span>
                {item.id === 'agent' && <span className="nav-live-dot" />}
              </button>
            );
          })}
        </nav>

        <div className="sidebar-spacer" />
        <div className="sidebar-note">
          <div className="note-icon"><ShieldCheck size={17} /></div>
          <strong>Controlled AI operations</strong>
          <p>Financial decisions stay grounded in your application data and services.</p>
        </div>
        <div className="sidebar-footer">
          <div className="avatar-small">{(email || 'U').charAt(0).toUpperCase()}</div>
          <div className="profile-copy"><strong>{email || 'Signed-in user'}</strong><span>Workspace member</span></div>
          <button className="icon-button logout-button" onClick={signOut} title="Sign out"><LogOut size={17} /></button>
        </div>
      </aside>

      {sidebarOpen && <button className="mobile-scrim" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />}

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="icon-button mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={20} /></button>
            <div className="breadcrumb"><span>Workspace</span><span className="crumb-slash">/</span><strong>{activeNav.label}</strong></div>
          </div>
          <div className="topbar-right">
            <div className="environment-pill"><span /> API-connected workspace</div>
            <div className="topbar-avatar">{(email || 'U').charAt(0).toUpperCase()}</div>
          </div>
        </header>

        <div className="page-content">
          <div className="page-heading">
            <div><div className="eyebrow">FINPILOT / WORKSPACE</div><h1>{activeNav.label}</h1><p>{activeNav.description}</p></div>
            <div className="heading-actions"><span className="date-chip"><Clock3 size={14} /> Live workspace</span></div>
          </div>

          {page === 'overview' && <OverviewPage onNavigate={setPage} />}
          {page === 'agent' && <AgentPage merchantId={merchantId} onMerchantChange={updateMerchant} notify={notify} />}
          {page === 'imports' && <ImportsPage merchantId={merchantId} onMerchantChange={updateMerchant} notify={notify} />}
          {page === 'documents' && <DocumentsPage notify={notify} />}
          {page === 'reports' && <ReportsPage merchantId={merchantId} onMerchantChange={updateMerchant} notify={notify} />}
        </div>
        <footer className="app-footer"><span>FinPilot-AI</span><span>Financial operations, made explainable.</span><span className="footer-version">Showcase build · v1.0</span></footer>
      </main>

      {toast && <div className={cx('toast', `toast-${toast.kind}`)}><span className="toast-indicator" />{toast.text}<button onClick={() => setToast(null)} aria-label="Dismiss"><X size={15} /></button></div>}
    </div>
  );
}

function AuthScreen({ onAuthenticated }: {
  onAuthenticated: (data: TokenResponse, email: string) => void;
}) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (mode === 'register') {
        const result = await registerRequest(username, email, password);
        setInfo(result.message || 'Account created. Sign in to continue.');
        setMode('login');
      } else {
        const data = await loginRequest(email, password);
        onAuthenticated(data, email);
      }
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-screen">
      <div className="auth-decoration auth-decoration-one" /><div className="auth-decoration auth-decoration-two" />
      <div className="auth-left-panel">
        <div className="auth-brand"><div className="brand-mark"><Activity size={22} /></div><div className="brand-name">FinPilot<span>-AI</span></div></div>
        <div className="auth-pitch">
          <div className="eyebrow eyebrow-light">FINANCIAL OPERATIONS INTELLIGENCE</div>
          <h1>See the signal.<br /><em>Understand the story.</em></h1>
          <p>Investigate payments, reconcile settlements and turn complex financial operations into clear, actionable intelligence.</p>
          <div className="auth-feature-list">
            <div><span><ScanSearch size={17} /></span><div><strong>Discrepancy investigation</strong><small>Find the gaps across transactions and settlements.</small></div></div>
            <div><span><Bot size={17} /></span><div><strong>Agentic workflows</strong><small>Coordinate specialized AI analysis with evidence.</small></div></div>
            <div><span><FileText size={17} /></span><div><strong>Evidence-backed reports</strong><small>Make findings clear, traceable and useful.</small></div></div>
          </div>
        </div>
        <div className="auth-footnote">BUILT FOR FINANCIAL OPERATIONS TEAMS</div>
      </div>
      <div className="auth-form-panel">
        <div className="auth-form-wrap">
          <div className="auth-form-mobile-brand"><div className="brand-mark"><Activity size={20} /></div><div className="brand-name">FinPilot<span>-AI</span></div></div>
          <div className="auth-welcome"><div className="eyebrow">WELCOME TO FINPILOT</div><h2>{mode === 'login' ? 'Sign in to your workspace' : 'Create your account'}</h2><p>{mode === 'login' ? 'Enter your credentials to continue to your financial workspace.' : 'Create an account to start exploring the demo workspace.'}</p></div>
          <div className="auth-mode-tabs"><button className={mode === 'login' ? 'selected' : ''} onClick={() => { setMode('login'); setError(''); }}>Sign in</button><button className={mode === 'register' ? 'selected' : ''} onClick={() => { setMode('register'); setError(''); setInfo(''); }}>Create account</button></div>
          {info && <div className="success-inline"><CheckCircle2 size={15} />{info}</div>}
          <form className="auth-form" onSubmit={submit}>
            {mode === 'register' && <label>Username<div className="input-wrap"><input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Your name" required minLength={2} /></div></label>}
            <label>Email address<div className="input-wrap"><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" required autoComplete="email" /></div></label>
            <label>Password<div className="input-wrap"><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" required minLength={6} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} /></div></label>
            {error && <div className="inline-error">{error}</div>}
            <button className="primary-button auth-submit" type="submit" disabled={loading}>{loading ? <span className="spinner" /> : mode === 'login' ? 'Sign in to workspace' : 'Create account'}<ArrowRight size={17} /></button>
          </form>
          <div className="auth-secure-note"><ShieldCheck size={15} /> Protected by your FinPilot-AI authentication service</div>
          <div className="auth-demo-note"><CircleHelp size={15} /><span>Demo environment. Register using your own test credentials or sign in with an existing account.</span></div>
        </div>
      </div>
    </div>
  );
}

function OverviewPage({ onNavigate }: { onNavigate: (page: Page) => void }) {
  const [health, setHealth] = useState<'checking' | 'online' | 'offline'>('checking');
  const [healthMessage, setHealthMessage] = useState('Checking FastAPI service…');

  const checkHealth = useCallback(async () => {
    setHealth('checking');
    try {
      const result = await apiRequest<{ message?: string }>('/', {}, false);
      setHealth('online');
      setHealthMessage(result.message || 'API responded successfully.');
    } catch {
      setHealth('offline');
      setHealthMessage('Could not reach the configured FastAPI server.');
    }
  }, []);

  useEffect(() => { void checkHealth(); }, [checkHealth]);

  return (
    <>
      <section className="welcome-banner">
        <div className="welcome-grid" />
        <div className="welcome-copy"><div className="banner-kicker"><Sparkles size={14} /> YOUR FINANCIAL COMMAND CENTER</div><h2>Good to have you back.</h2><p>Bring your financial data together, ask better questions and let your AI workflow investigate the details.</p><div className="welcome-actions"><button className="banner-button" onClick={() => onNavigate('agent')}>Launch an agent task <ArrowRight size={16} /></button><button className="banner-link" onClick={() => onNavigate('imports')}>Import financial data <ArrowUpRight size={15} /></button></div></div>
        <div className="banner-art" aria-hidden="true"><div className="art-orbit orbit-one" /><div className="art-orbit orbit-two" /><div className="art-core"><Activity size={36} /></div><div className="art-chip chip-a"><span className="chip-dot green" />Payments</div><div className="art-chip chip-b"><span className="chip-dot blue" />AI insights</div><div className="art-chip chip-c"><span className="chip-dot amber" />Settlements</div></div>
      </section>

      <div className="section-header"><div><h3>Workspace pulse</h3><p>Live connection status and available capabilities.</p></div><button className="subtle-button" onClick={checkHealth}><RefreshCw size={14} /> Refresh status</button></div>
      <div className="overview-grid">
        <div className="panel api-status-card"><div className="panel-topline"><div className="metric-icon blue-icon"><Activity size={19} /></div><span className={cx('status-badge', `status-${health}`)}><i />{health === 'online' ? 'Connected' : health === 'offline' ? 'Unavailable' : 'Checking'}</span></div><div className="panel-label">FastAPI service</div><div className="api-status-message">{healthMessage}</div><div className="panel-bottom"><span>GET /</span><button onClick={() => { void checkHealth(); }}>Test connection <ArrowUpRight size={13} /></button></div></div>
        <InfoMetric icon={<CreditCard size={19} />} label="Transaction analytics" value="API not exposed" detail="Add analytics endpoints to show live KPIs." tone="violet" />
        <InfoMetric icon={<ScanSearch size={19} />} label="Reconciliation cases" value="API not exposed" detail="Case-list endpoint is not in the shared API yet." tone="amber" />
        <InfoMetric icon={<FileText size={19} />} label="Generated reports" value="By task ID" detail="Retrieve the output using a task identifier." tone="green" />
      </div>

      <div className="section-header section-header-spaced"><div><h3>Get started</h3><p>Core capabilities currently available through your backend.</p></div><span className="micro-label">5 WORKFLOWS</span></div>
      <div className="capability-grid">
        <CapabilityCard icon={<Bot size={20} />} tint="violet" number="01" title="Run an investigation" description="Submit a payment investigation, reconciliation or financial research task to your LangGraph workflow." action="Open agent workspace" onClick={() => onNavigate('agent')} />
        <CapabilityCard icon={<Database size={20} />} tint="blue" number="02" title="Load merchant data" description="Import merchants from CSV, then load the financial transactions and settlement records for each merchant." action="Go to data imports" onClick={() => onNavigate('imports')} />
        <CapabilityCard icon={<Files size={20} />} tint="green" number="03" title="Add knowledge documents" description="Upload PDF and other supported files to your document ingestion pipeline." action="Open knowledge base" onClick={() => onNavigate('documents')} />
        <CapabilityCard icon={<FileText size={20} />} tint="amber" number="04" title="Review agent reports" description="Fetch a completed task result and inspect the structured report produced by your workflow." action="View reports" onClick={() => onNavigate('reports')} />
      </div>
      <div className="notice-card"><div className="notice-icon"><CircleHelp size={18} /></div><div><strong>Why are some metrics unavailable?</strong><p>Your current FastAPI routes do not yet expose dashboard aggregation, transaction listing or reconciliation case listing endpoints. FinPilot-AI keeps those areas honest rather than showing fabricated financial figures.</p></div></div>
    </>
  );
}

function InfoMetric({ icon, label, value, detail, tone }: { icon: ReactNode; label: string; value: string; detail: string; tone: string }) {
  return <div className="panel metric-card"><div className={cx('metric-icon', `${tone}-icon`)}>{icon}</div><div className="panel-label">{label}</div><div className="metric-value metric-placeholder">{value}</div><div className="metric-detail">{detail}</div></div>;
}

function CapabilityCard({ icon, tint, number, title, description, action, onClick }: { icon: ReactNode; tint: string; number: string; title: string; description: string; action: string; onClick: () => void }) {
  return <button className="capability-card" onClick={onClick}><div className="capability-top"><div className={`metric-icon ${tint}-icon`}>{icon}</div><span>{number}</span></div><h4>{title}</h4><p>{description}</p><div className="capability-action">{action}<ArrowRight size={15} /></div></button>;
}

function MerchantIdField({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  return <label className="field-label">Merchant ID <span className="field-required">Required</span><input className="text-input mono-input" value={value} onChange={(event) => onChange(event.target.value)} placeholder="Paste the merchant UUID from your database" /></label>;
}

function AgentPage({ merchantId, onMerchantChange, notify }: { merchantId: string; onMerchantChange: (value: string) => void; notify: (kind: 'success' | 'error' | 'info', text: string) => void }) {
  const [taskType, setTaskType] = useState<TaskType>('reconciliation');
  const [prompt, setPrompt] = useState('Investigate settlement discrepancies for this merchant. Identify missing settlement items, amount mismatches, duplicate or unmatched items, and currency mismatches. Summarize the evidence and recommended next steps.');
  const [inputData, setInputData] = useState('{}');
  const [task, setTask] = useState<AgentTaskCreated | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const selectedTask = TASK_OPTIONS.find((option) => option.value === taskType)!;

  const submitTask = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    let parsedInput: Record<string, unknown>;
    try {
      const parsed: unknown = JSON.parse(inputData || '{}');
      if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') throw new Error('Input data must be a JSON object.');
      parsedInput = parsed as Record<string, unknown>;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Input data must be valid JSON.');
      return;
    }
    if (!merchantId.trim()) { setError('Enter a merchant UUID before submitting a task.'); return; }
    setSubmitting(true);
    try {
      const result = await apiRequest<AgentTaskCreated>('/agent-tasks', {
        method: 'POST',
        headers: { 'Idempotency-Key': crypto.randomUUID() },
        body: JSON.stringify({ merchant_id: merchantId.trim(), task_type: taskType, prompt, input_data: parsedInput }),
      });
      setTask(result);
      notify('success', 'Agent task accepted by the API.');
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="content-columns agent-layout">
      <section className="panel form-panel">
        <div className="panel-heading"><div><div className="eyebrow">LANGGRAPH ORCHESTRATION</div><h3>Launch an agent task</h3><p>Submit a task to your backend workflow. The API responds with a task ID for tracking.</p></div><div className="heading-icon purple-heading"><Bot size={21} /></div></div>
        <form onSubmit={submitTask} className="stacked-form">
          <MerchantIdField value={merchantId} onChange={onMerchantChange} />
          <label className="field-label">Task type<select className="text-input" value={taskType} onChange={(e) => setTaskType(e.target.value as TaskType)}>{TASK_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select><span className="field-hint">{selectedTask.detail}</span></label>
          <label className="field-label">Investigation prompt<textarea className="text-input textarea" value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={5} minLength={5} maxLength={10000} required /><span className="field-hint">Describe the question and what the agent should investigate. {prompt.length}/10,000 characters.</span></label>
          <label className="field-label">Additional input data <span className="optional-label">Optional JSON</span><textarea className="text-input code-textarea" value={inputData} onChange={(e) => setInputData(e.target.value)} rows={3} spellCheck={false} /></label>
          {error && <div className="inline-error">{error}</div>}
          <div className="form-actions"><span className="form-security"><ShieldCheck size={14} /> Protected write operation</span><button className="primary-button" type="submit" disabled={submitting}>{submitting ? <span className="spinner" /> : <Send size={16} />} Submit task</button></div>
        </form>
      </section>
      <div className="agent-side-column">
        <section className="panel task-info-panel"><div className="panel-title-row"><h3>Task lifecycle</h3><span className="small-status"><i /> Async</span></div><div className="lifecycle-list"><LifecycleStep n="01" title="Task accepted" detail="FastAPI validates the request and returns a task ID." active /><LifecycleStep n="02" title="Worker execution" detail="Your Celery worker dispatches the agent workflow." /><LifecycleStep n="03" title="Graph orchestration" detail="Specialist nodes investigate and evaluate findings." /><LifecycleStep n="04" title="Report persisted" detail="Retrieve the result using the task ID." last /></div></section>
        <section className="panel response-panel"><div className="panel-title-row"><h3>Latest submission</h3><span className="micro-label">API RESPONSE</span></div>{task ? <><div className="task-success"><CheckCircle2 size={18} /><span>Task accepted</span></div><div className="response-kv"><span>Task ID</span><code>{task.task_id}</code><button className="copy-button" onClick={() => { void navigator.clipboard.writeText(task.task_id); notify('success', 'Task ID copied.'); }}>Copy</button></div><div className="response-kv"><span>Status</span><strong className="status-text">{task.status}</strong></div><p className="response-message">{task.message}</p><button className="text-button" onClick={() => { localStorage.setItem('finpilot_last_task_id', task.task_id); notify('info', 'Task ID saved for the Reports page.'); }}>Save task ID for reports <ArrowRight size={14} /></button></> : <div className="empty-response"><div className="empty-icon"><Bot size={23} /></div><strong>No task submitted yet</strong><p>Your API response, task ID and current status will appear here.</p></div>}</section>
      </div>
    </div>
  );
}

function LifecycleStep({ n, title, detail, active, last }: { n: string; title: string; detail: string; active?: boolean; last?: boolean }) {
  return <div className={cx('lifecycle-step', active && 'lifecycle-active', last && 'lifecycle-last')}><div className="lifecycle-marker">{active ? <span /> : n}</div><div><strong>{title}</strong><p>{detail}</p></div></div>;
}

function ImportsPage({ merchantId, onMerchantChange, notify }: { merchantId: string; onMerchantChange: (value: string) => void; notify: (kind: 'success' | 'error' | 'info', text: string) => void }) {
  const [merchantFile, setMerchantFile] = useState<File | null>(null);
  const [financialFile, setFinancialFile] = useState<File | null>(null);
  const [merchantLoading, setMerchantLoading] = useState(false);
  const [financialLoading, setFinancialLoading] = useState(false);
  const [merchantResult, setMerchantResult] = useState<unknown>(null);
  const [financialResult, setFinancialResult] = useState<unknown>(null);
  const [error, setError] = useState('');

  const uploadMerchants = async (event: FormEvent) => {
    event.preventDefault();
    if (!merchantFile) return;
    setError(''); setMerchantLoading(true); setMerchantResult(null);
    const data = new FormData(); data.append('file', merchantFile);
    try {
      const result = await apiRequest<unknown>('/merchants/import', { method: 'POST', body: data });
      setMerchantResult(result); notify('success', 'Merchant CSV import request completed.');
    } catch (err) { setError(friendlyError(err)); } finally { setMerchantLoading(false); }
  };

  const uploadFinancial = async (event: FormEvent) => {
    event.preventDefault();
    if (!financialFile) return;
    if (!merchantId.trim()) { setError('Enter the merchant UUID that owns this CSV.'); return; }
    setError(''); setFinancialLoading(true); setFinancialResult(null);
    const data = new FormData(); data.append('file', financialFile);
    try {
      const result = await apiRequest<unknown>(`/merchants/${encodeURIComponent(merchantId.trim())}/transactions/import`, { method: 'POST', body: data });
      setFinancialResult(result); notify('success', 'Financial CSV import completed.');
    } catch (err) { setError(friendlyError(err)); } finally { setFinancialLoading(false); }
  };

  return (
    <>
      <div className="notice-card import-notice"><div className="notice-icon"><CircleHelp size={18} /></div><div><strong>Import sequence matters</strong><p>First import your merchants CSV. Then copy a merchant UUID from your database and import the matching financial CSV for that merchant. Your current financial import endpoint accepts one merchant ID per upload.</p></div></div>
      {error && <div className="inline-error global-error">{error}</div>}
      <div className="content-columns import-columns">
        <section className="panel form-panel"><div className="panel-heading"><div><div className="eyebrow">STEP 01 · MERCHANTS</div><h3>Import merchant records</h3><p>Create merchant records from your merchant seed CSV.</p></div><div className="heading-icon blue-heading"><Building2 size={21} /></div></div>
          <form className="stacked-form" onSubmit={uploadMerchants}><FilePicker file={merchantFile} onChange={setMerchantFile} accept=".csv,text/csv" hint="Expected columns: name, external_ref, currency" /><div className="form-actions"><span className="form-security"><ShieldCheck size={14} /> Merchant import endpoint</span><button className="primary-button" disabled={!merchantFile || merchantLoading}>{merchantLoading ? <span className="spinner" /> : <UploadCloud size={16} />} Import merchants</button></div></form>
          {merchantResult !== null && <ResultPanel title="Merchant import response" data={merchantResult} />}
        </section>
        <section className="panel form-panel"><div className="panel-heading"><div><div className="eyebrow">STEP 02 · FINANCIAL DATA</div><h3>Import transactions & settlements</h3><p>Load transaction, settlement and settlement-item records for one merchant.</p></div><div className="heading-icon green-heading"><WalletCards size={21} /></div></div>
          <form className="stacked-form" onSubmit={uploadFinancial}><MerchantIdField value={merchantId} onChange={onMerchantChange} /><FilePicker file={financialFile} onChange={setFinancialFile} accept=".csv,text/csv" hint="Your combined financial CSV with transaction and settlement columns." /><div className="form-actions"><span className="form-security"><ShieldCheck size={14} /> Requires write access</span><button className="primary-button" disabled={!financialFile || financialLoading}>{financialLoading ? <span className="spinner" /> : <UploadCloud size={16} />} Import financial data</button></div></form>
          {financialResult !== null && <ResultPanel title="Financial import response" data={financialResult} />}
        </section>
      </div>
      <div className="small-callout"><strong>CSV tip</strong><span>Do not include server-generated fields such as database IDs or timestamps unless your importer explicitly supports them. Keep each financial CSV scoped to the merchant ID entered above.</span></div>
    </>
  );
}

function FilePicker({ file, onChange, accept, hint }: { file: File | null; onChange: (file: File | null) => void; accept: string; hint: string }) {
  return <div className="file-picker"><label className={cx('file-drop', file && 'file-selected')}><input type="file" accept={accept} onChange={(e) => onChange(e.target.files?.[0] || null)} /><div className="file-drop-icon"><UploadCloud size={22} /></div><div><strong>{file ? file.name : 'Choose a CSV file'}</strong><span>{file ? `${(file.size / 1024).toFixed(1)} KB · Ready to upload` : 'Browse your computer or drop a file here'}</span></div><span className="browse-label">Browse</span></label><span className="field-hint">{hint}</span>{file && <button type="button" className="remove-file" onClick={() => onChange(null)}><X size={13} /> Remove file</button>}</div>;
}

function DocumentsPage({ notify }: { notify: (kind: 'success' | 'error' | 'info', text: string) => void }) {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const upload = async (event: FormEvent) => {
    event.preventDefault();
    if (!files.length) return;
    setLoading(true); setError(''); setMessage('');
    const data = new FormData();
    files.forEach((file) => data.append('files', file));
    try {
      const response = await apiRequest<unknown>('/documents/UploadDocument', { method: 'POST', body: data });
      setMessage(typeof response === 'string' ? response : JSON.stringify(response ?? { message: 'Upload request completed.' }, null, 2));
      setFiles([]); notify('success', 'Document upload request completed.');
    } catch (err) { setError(friendlyError(err)); } finally { setLoading(false); }
  };

  return <div className="content-columns document-layout"><section className="panel form-panel"><div className="panel-heading"><div><div className="eyebrow">RETRIEVAL-AUGMENTED GENERATION</div><h3>Add knowledge documents</h3><p>Upload internal financial or operational documents to your existing document ingestion service.</p></div><div className="heading-icon blue-heading"><Files size={21} /></div></div><form className="stacked-form" onSubmit={upload}><div className="field-label">Select documents</div><label className="multi-file-drop"><input type="file" multiple onChange={(e) => setFiles(Array.from(e.target.files || []))} /><div className="multi-file-icon"><UploadCloud size={27} /></div><strong>Drop documents here or browse</strong><span>Choose one or more files supported by your backend.</span><span className="browse-label">Browse files</span></label>{files.length > 0 && <div className="selected-file-list">{files.map((file) => <div key={`${file.name}-${file.size}`}><FileText size={15} /><span>{file.name}</span><small>{(file.size / 1024).toFixed(0)} KB</small></div>)}</div>}<div className="form-actions"><span className="form-security"><ShieldCheck size={14} /> Requires write access</span><button className="primary-button" disabled={!files.length || loading}>{loading ? <span className="spinner" /> : <UploadCloud size={16} />} Upload documents</button></div></form>{error && <div className="inline-error">{error}</div>}{message && <div className="success-response"><CheckCircle2 size={17} /><pre>{message}</pre></div>}</section><section className="panel info-panel"><div className="info-panel-icon"><Database size={22} /></div><h3>From document to evidence</h3><p>Your existing backend owns file processing. This page simply sends selected files to the `DocumentUpload` endpoint.</p><div className="mini-flow"><div><span>01</span><strong>Upload</strong><small>FastAPI receives files</small></div><ArrowRight size={16} /><div><span>02</span><strong>Process</strong><small>Extract and chunk text</small></div><ArrowRight size={16} /><div><span>03</span><strong>Retrieve</strong><small>Use context in agent tasks</small></div></div><div className="info-footnote"><CircleHelp size={15} /> The shared API does not currently include document listing or deletion endpoints.</div></section></div>;
}

function ReportsPage({ merchantId, onMerchantChange, notify }: { merchantId: string; onMerchantChange: (value: string) => void; notify: (kind: 'success' | 'error' | 'info', text: string) => void }) {
  const savedTask = localStorage.getItem('finpilot_last_task_id') || '';
  const [taskId, setTaskId] = useState(savedTask);
  const [reportData, setReportData] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState<'result' | 'list'>('result');

  const fetchReport = async (event: FormEvent) => {
    event.preventDefault();
    if (!taskId.trim()) { setError('Enter a task UUID.'); return; }
    if (mode === 'list' && !merchantId.trim()) { setError('Enter the merchant UUID to list reports for this task.'); return; }
    setLoading(true); setError(''); setReportData(null);
    try {
      const path = mode === 'result'
        ? `/reports/${encodeURIComponent(taskId.trim())}/result`
        : `/reports/tasks/${encodeURIComponent(taskId.trim())}?merchant_id=${encodeURIComponent(merchantId.trim())}`;
      const data = await apiRequest<unknown>(path);
      setReportData(data); notify('success', 'Report data retrieved.');
    } catch (err) { setError(friendlyError(err)); } finally { setLoading(false); }
  };

  return <div className="content-columns report-layout"><section className="panel form-panel"><div className="panel-heading"><div><div className="eyebrow">AGENT OUTPUTS</div><h3>Retrieve a task report</h3><p>Use the task ID returned when an agent task was submitted.</p></div><div className="heading-icon amber-heading"><FileText size={21} /></div></div><form className="stacked-form" onSubmit={fetchReport}><div className="segmented-control"><button type="button" className={mode === 'result' ? 'active' : ''} onClick={() => setMode('result')}>Task result</button><button type="button" className={mode === 'list' ? 'active' : ''} onClick={() => setMode('list')}>Saved reports</button></div><label className="field-label">Task ID<input className="text-input mono-input" value={taskId} onChange={(e) => setTaskId(e.target.value)} placeholder="Paste task UUID" /></label>{mode === 'list' && <MerchantIdField value={merchantId} onChange={onMerchantChange} />}<div className="form-actions"><span className="form-security"><ShieldCheck size={14} /> Read operation</span><button className="primary-button" disabled={loading}>{loading ? <span className="spinner" /> : <ArrowDownToLine size={16} />} Retrieve report</button></div></form>{error && <div className="inline-error">{error}</div>}</section><section className="panel report-viewer"><div className="panel-title-row"><div><h3>Report preview</h3><p>Structured response from your backend</p></div><span className="micro-label">JSON VIEW</span></div>{reportData !== null ? <ResultPanel title="API response" data={reportData} /> : <div className="empty-response report-empty"><div className="empty-icon"><FileText size={23} /></div><strong>No report loaded</strong><p>Retrieve a task result or saved report to see the report payload here.</p></div>}</section></div>;
}

function ResultPanel({ title, data }: { title: string; data: unknown }) {
  const json = useMemo(() => JSON.stringify(data, null, 2), [data]);
  return <div className="result-panel"><div className="result-panel-head"><strong>{title}</strong><button className="copy-button" onClick={() => { void navigator.clipboard.writeText(json); }}>Copy JSON</button></div><pre>{json}</pre></div>;
}

export default App;
