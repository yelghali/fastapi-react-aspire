/**
 * Projects page - GitHub-integrated project management dashboard.
 *
 * Features:
 * - Repository overview with stats
 * - Issue list with state/label filtering
 * - Create new issues
 * - Pull request list
 * - Milestone progress tracking
 * - All API calls traced via OpenTelemetry
 */

import type { MetaFunction } from "react-router";
import { Link } from "react-router";
import { useState, useEffect, useCallback } from "react";
import {
  HiOutlineRefresh,
  HiOutlinePlus,
  HiOutlineExternalLink,
  HiOutlineStar,
  HiOutlineExclamationCircle,
} from "react-icons/hi";
import { traced } from "../../lib/telemetry";

export const meta: MetaFunction = () => {
  return [
    { title: "Projects - FastAPI React Aspire Starter" },
    {
      name: "description",
      content: "GitHub-integrated project management dashboard",
    },
  ];
};

// ── Types ─────────────────────────────────────────────────────────

interface GitHubUser {
  login: string;
  avatar_url: string;
  html_url: string;
}

interface GitHubLabel {
  name: string;
  color: string;
  description: string | null;
}

interface GitHubMilestone {
  number: number;
  title: string;
  description: string | null;
  state: string;
  open_issues: number;
  closed_issues: number;
  due_on: string | null;
  html_url: string;
}

interface GitHubIssue {
  number: number;
  title: string;
  body: string | null;
  state: string;
  labels: GitHubLabel[];
  assignees: GitHubUser[];
  user: GitHubUser | null;
  milestone: GitHubMilestone | null;
  comments: number;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  html_url: string;
  pull_request_url: string | null;
}

interface GitHubPullRequest {
  number: number;
  title: string;
  state: string;
  user: GitHubUser | null;
  labels: GitHubLabel[];
  created_at: string;
  updated_at: string;
  merged_at: string | null;
  html_url: string;
  draft: boolean;
}

interface RepoOverview {
  full_name: string;
  description: string | null;
  html_url: string;
  stars: number;
  forks: number;
  open_issues_count: number;
  language: string | null;
  topics: string[];
  default_branch: string;
  updated_at: string | null;
}

// ── Tab type ──────────────────────────────────────────────────────

type TabName = "issues" | "pulls" | "milestones";

// ── Component ─────────────────────────────────────────────────────

export default function Projects() {
  const [overview, setOverview] = useState<RepoOverview | null>(null);
  const [issues, setIssues] = useState<GitHubIssue[]>([]);
  const [pulls, setPulls] = useState<GitHubPullRequest[]>([]);
  const [milestones, setMilestones] = useState<GitHubMilestone[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [activeTab, setActiveTab] = useState<TabName>("issues");
  const [issueState, setIssueState] = useState("open");
  const [prState, setPrState] = useState("open");

  // Create issue form
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");

  // ── Data fetching ───────────────────────────────────────────────

  const fetchOverview = useCallback(async () => {
    try {
      const resp = await traced("fetchOverview", () =>
        fetch("/api/projects/overview"),
      );
      if (!resp.ok) throw new Error(`Failed to fetch overview: ${resp.statusText}`);
      setOverview(await resp.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch overview");
    }
  }, []);

  const fetchIssues = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await traced("fetchIssues", () =>
        fetch(`/api/projects/issues?state=${issueState}&per_page=50`),
      );
      if (!resp.ok) throw new Error(`Failed to fetch issues: ${resp.statusText}`);
      setIssues(await resp.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch issues");
    } finally {
      setLoading(false);
    }
  }, [issueState]);

  const fetchPulls = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await traced("fetchPulls", () =>
        fetch(`/api/projects/pulls?state=${prState}&per_page=50`),
      );
      if (!resp.ok) throw new Error(`Failed to fetch PRs: ${resp.statusText}`);
      setPulls(await resp.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch PRs");
    } finally {
      setLoading(false);
    }
  }, [prState]);

  const fetchMilestones = useCallback(async () => {
    setLoading(true);
    try {
      const resp = await traced("fetchMilestones", () =>
        fetch("/api/projects/milestones?state=all"),
      );
      if (!resp.ok) throw new Error(`Failed to fetch milestones: ${resp.statusText}`);
      setMilestones(await resp.json());
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to fetch milestones",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  useEffect(() => {
    if (activeTab === "issues") fetchIssues();
    else if (activeTab === "pulls") fetchPulls();
    else if (activeTab === "milestones") fetchMilestones();
  }, [activeTab, fetchIssues, fetchPulls, fetchMilestones]);

  // ── Create issue ────────────────────────────────────────────────

  const handleCreateIssue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      const resp = await traced("createIssue", () =>
        fetch("/api/projects/issues", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title: newTitle, body: newBody }),
        }),
      );
      if (!resp.ok) throw new Error(`Failed to create issue: ${resp.statusText}`);
      setNewTitle("");
      setNewBody("");
      setShowCreateForm(false);
      fetchIssues();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create issue");
    }
  };

  // ── Refresh current tab ─────────────────────────────────────────

  const refresh = () => {
    setError(null);
    fetchOverview();
    if (activeTab === "issues") fetchIssues();
    else if (activeTab === "pulls") fetchPulls();
    else fetchMilestones();
  };

  // ── Render ──────────────────────────────────────────────────────

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-zinc-200 dark:border-zinc-800">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              ← Home
            </Link>
            <h1 className="text-xl font-bold">Projects</h1>
          </div>
          <button
            onClick={refresh}
            className="p-2 text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
            title="Refresh"
          >
            <HiOutlineRefresh
              className={`w-5 h-5 ${loading ? "animate-spin" : ""}`}
            />
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-4xl mx-auto px-4 py-8 w-full">
        {/* Repo overview card */}
        {overview && <OverviewCard overview={overview} />}

        {/* Tabs */}
        <div className="flex gap-1 border-b border-zinc-200 dark:border-zinc-700 mb-6">
          {(["issues", "pulls", "milestones"] as TabName[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium capitalize border-b-2 transition-colors ${
                activeTab === tab
                  ? "border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400"
                  : "border-transparent text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
              }`}
            >
              {tab === "pulls" ? "Pull Requests" : tab}
            </button>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg">
            {error}
          </div>
        )}

        {/* Issues tab */}
        {activeTab === "issues" && (
          <>
            {/* Controls */}
            <div className="flex items-center justify-between mb-4">
              <StateFilter value={issueState} onChange={setIssueState} />
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors flex items-center gap-1"
              >
                <HiOutlinePlus className="w-4 h-4" />
                New Issue
              </button>
            </div>

            {/* Create form */}
            {showCreateForm && (
              <form
                onSubmit={handleCreateIssue}
                className="mb-6 p-4 border border-zinc-200 dark:border-zinc-700 rounded-lg space-y-3"
              >
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="Issue title"
                  className="w-full px-4 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <textarea
                  value={newBody}
                  onChange={(e) => setNewBody(e.target.value)}
                  placeholder="Description (markdown supported)"
                  rows={4}
                  className="w-full px-4 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="flex gap-2 justify-end">
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="px-4 py-2 text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700"
                  >
                    Create Issue
                  </button>
                </div>
              </form>
            )}

            {/* Issue list */}
            {loading && issues.length === 0 ? (
              <Loading />
            ) : issues.length === 0 ? (
              <Empty message="No issues found." />
            ) : (
              <div className="space-y-2">
                {issues.map((issue) => (
                  <IssueRow key={issue.number} issue={issue} />
                ))}
              </div>
            )}
          </>
        )}

        {/* Pull Requests tab */}
        {activeTab === "pulls" && (
          <>
            <div className="mb-4">
              <StateFilter value={prState} onChange={setPrState} />
            </div>
            {loading && pulls.length === 0 ? (
              <Loading />
            ) : pulls.length === 0 ? (
              <Empty message="No pull requests found." />
            ) : (
              <div className="space-y-2">
                {pulls.map((pr) => (
                  <PullRequestRow key={pr.number} pr={pr} />
                ))}
              </div>
            )}
          </>
        )}

        {/* Milestones tab */}
        {activeTab === "milestones" && (
          <>
            {loading && milestones.length === 0 ? (
              <Loading />
            ) : milestones.length === 0 ? (
              <Empty message="No milestones found." />
            ) : (
              <div className="space-y-4">
                {milestones.map((ms) => (
                  <MilestoneCard key={ms.number} milestone={ms} />
                ))}
              </div>
            )}
          </>
        )}

        {/* Tip */}
        <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm">
          <p className="text-blue-800 dark:text-blue-200">
            <strong>💡 Tip:</strong> This dashboard reads live data from the
            GitHub API. Set the <code>APP_GITHUB_TOKEN</code> environment
            variable to enable creating issues and get higher rate limits.
          </p>
        </div>
      </main>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────

function OverviewCard({ overview }: { overview: RepoOverview }) {
  return (
    <div className="mb-6 p-4 border border-zinc-200 dark:border-zinc-700 rounded-lg">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold">{overview.full_name}</h2>
          {overview.description && (
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">
              {overview.description}
            </p>
          )}
          {overview.topics.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {overview.topics.map((t) => (
                <span
                  key={t}
                  className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 rounded-full"
                >
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
        <a
          href={overview.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
        >
          <HiOutlineExternalLink className="w-5 h-5" />
        </a>
      </div>
      <div className="flex gap-6 mt-3 text-sm text-zinc-500 dark:text-zinc-400">
        <span className="flex items-center gap-1">
          <HiOutlineStar className="w-4 h-4" /> {overview.stars}
        </span>
        <span>🍴 {overview.forks}</span>
        <span className="flex items-center gap-1">
          <HiOutlineExclamationCircle className="w-4 h-4" />{" "}
          {overview.open_issues_count} open
        </span>
        {overview.language && <span>🔤 {overview.language}</span>}
      </div>
    </div>
  );
}

function StateFilter({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex gap-1 text-sm">
      {["open", "closed", "all"].map((s) => (
        <button
          key={s}
          onClick={() => onChange(s)}
          className={`px-3 py-1 rounded-full capitalize ${
            value === s
              ? "bg-zinc-200 dark:bg-zinc-700 text-zinc-900 dark:text-zinc-100 font-medium"
              : "text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
          }`}
        >
          {s}
        </button>
      ))}
    </div>
  );
}

function IssueRow({ issue }: { issue: GitHubIssue }) {
  return (
    <div className="flex items-start gap-3 p-3 border border-zinc-200 dark:border-zinc-700 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
      <span
        className={`mt-1 w-3 h-3 rounded-full flex-shrink-0 ${
          issue.state === "open" ? "bg-green-500" : "bg-purple-500"
        }`}
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <a
            href={issue.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium hover:text-blue-600 dark:hover:text-blue-400 truncate"
          >
            {issue.title}
          </a>
        </div>
        <div className="flex flex-wrap items-center gap-2 mt-1">
          <span className="text-xs text-zinc-400">#{issue.number}</span>
          {issue.labels.map((lb) => (
            <span
              key={lb.name}
              className="px-1.5 py-0.5 text-xs rounded-full border border-zinc-200 dark:border-zinc-600"
              style={{
                backgroundColor: `#${lb.color}20`,
                color: `#${lb.color}`,
              }}
            >
              {lb.name}
            </span>
          ))}
          {issue.assignees.map((a) => (
            <img
              key={a.login}
              src={a.avatar_url}
              alt={a.login}
              title={a.login}
              className="w-5 h-5 rounded-full"
            />
          ))}
          {issue.comments > 0 && (
            <span className="text-xs text-zinc-400">
              💬 {issue.comments}
            </span>
          )}
          <span className="text-xs text-zinc-400 ml-auto">
            {new Date(issue.updated_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

function PullRequestRow({ pr }: { pr: GitHubPullRequest }) {
  return (
    <div className="flex items-start gap-3 p-3 border border-zinc-200 dark:border-zinc-700 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
      <span
        className={`mt-1 w-3 h-3 rounded-full flex-shrink-0 ${
          pr.merged_at
            ? "bg-purple-500"
            : pr.state === "open"
              ? "bg-green-500"
              : "bg-red-500"
        }`}
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <a
            href={pr.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium hover:text-blue-600 dark:hover:text-blue-400 truncate"
          >
            {pr.title}
          </a>
          {pr.draft && (
            <span className="text-xs px-1.5 py-0.5 bg-zinc-200 dark:bg-zinc-700 rounded text-zinc-500">
              Draft
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 mt-1 text-xs text-zinc-400">
          <span>#{pr.number}</span>
          {pr.user && <span>by {pr.user.login}</span>}
          {pr.labels.map((lb) => (
            <span
              key={lb.name}
              className="px-1.5 py-0.5 rounded-full border border-zinc-200 dark:border-zinc-600"
              style={{
                backgroundColor: `#${lb.color}20`,
                color: `#${lb.color}`,
              }}
            >
              {lb.name}
            </span>
          ))}
          <span className="ml-auto">
            {new Date(pr.updated_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

function MilestoneCard({ milestone }: { milestone: GitHubMilestone }) {
  const total = milestone.open_issues + milestone.closed_issues;
  const pct = total > 0 ? Math.round((milestone.closed_issues / total) * 100) : 0;
  return (
    <div className="p-4 border border-zinc-200 dark:border-zinc-700 rounded-lg">
      <div className="flex items-center justify-between">
        <a
          href={milestone.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="font-semibold hover:text-blue-600 dark:hover:text-blue-400"
        >
          {milestone.title}
        </a>
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${
            milestone.state === "open"
              ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
              : "bg-zinc-200 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300"
          }`}
        >
          {milestone.state}
        </span>
      </div>
      {milestone.description && (
        <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">
          {milestone.description}
        </p>
      )}
      {/* Progress bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs text-zinc-500 mb-1">
          <span>{pct}% complete</span>
          <span>
            {milestone.closed_issues}/{total} issues
          </span>
        </div>
        <div className="w-full h-2 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 rounded-full transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
      {milestone.due_on && (
        <p className="text-xs text-zinc-400 mt-2">
          Due: {new Date(milestone.due_on).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}

function Loading() {
  return <div className="text-center py-12 text-zinc-500">Loading...</div>;
}

function Empty({ message }: { message: string }) {
  return (
    <div className="text-center py-12 text-zinc-500">{message}</div>
  );
}
