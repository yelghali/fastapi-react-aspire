"""Business logic for the Projects module (GitHub API integration).

Provides read/write access to GitHub issues, pull requests, milestones,
and repository metadata for project management.
"""

import logging

import httpx

from ...common.tracer import trace
from .schemas import (
    GitHubComment,
    GitHubIssue,
    GitHubIssueCreate,
    GitHubIssueUpdate,
    GitHubLabel,
    GitHubMilestone,
    GitHubPullRequest,
    GitHubUser,
    RepoOverview,
)

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"


class ProjectService:
    """Service for GitHub-backed project management.

    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        token: Optional GitHub personal access token for higher rate limits
               and write access. Unauthenticated requests are read-only with
               lower rate limits.
    """

    def __init__(self, owner: str, repo: str, token: str = "") -> None:
        self._owner = owner
        self._repo = repo
        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url=GITHUB_API_BASE,
            headers=headers,
            timeout=30.0,
        )

    @property
    def _repo_path(self) -> str:
        return f"/repos/{self._owner}/{self._repo}"

    # ── Repo overview ──────────────────────────────────────────────

    @trace
    async def get_repo_overview(self) -> RepoOverview:
        """Get repository metadata and stats."""
        resp = await self._client.get(self._repo_path)
        resp.raise_for_status()
        data = resp.json()
        return RepoOverview(
            full_name=data["full_name"],
            description=data.get("description"),
            html_url=data["html_url"],
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
            language=data.get("language"),
            topics=data.get("topics", []),
            default_branch=data.get("default_branch", "main"),
            updated_at=data.get("updated_at"),
        )

    # ── Issues ─────────────────────────────────────────────────────

    @trace
    async def list_issues(
        self,
        state: str = "open",
        labels: str = "",
        assignee: str = "",
        milestone: str = "",
        per_page: int = 30,
        page: int = 1,
    ) -> list[GitHubIssue]:
        """List issues (excludes pull requests)."""
        params: dict[str, str | int] = {
            "state": state,
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }
        if labels:
            params["labels"] = labels
        if assignee:
            params["assignee"] = assignee
        if milestone:
            params["milestone"] = milestone

        resp = await self._client.get(f"{self._repo_path}/issues", params=params)
        resp.raise_for_status()

        issues: list[GitHubIssue] = []
        for item in resp.json():
            # GitHub API returns PRs in /issues — skip them
            if "pull_request" in item:
                continue
            issues.append(self._parse_issue(item))
        return issues

    @trace
    async def get_issue(self, issue_number: int) -> GitHubIssue:
        """Get a single issue by number."""
        resp = await self._client.get(f"{self._repo_path}/issues/{issue_number}")
        resp.raise_for_status()
        return self._parse_issue(resp.json())

    @trace
    async def create_issue(self, issue: GitHubIssueCreate) -> GitHubIssue:
        """Create a new issue. Requires a GitHub token with repo scope."""
        payload: dict = {"title": issue.title}
        if issue.body:
            payload["body"] = issue.body
        if issue.labels:
            payload["labels"] = issue.labels
        if issue.assignees:
            payload["assignees"] = issue.assignees
        if issue.milestone is not None:
            payload["milestone"] = issue.milestone

        resp = await self._client.post(f"{self._repo_path}/issues", json=payload)
        resp.raise_for_status()
        return self._parse_issue(resp.json())

    @trace
    async def update_issue(
        self, issue_number: int, update: GitHubIssueUpdate
    ) -> GitHubIssue:
        """Update an existing issue. Requires a GitHub token with repo scope."""
        payload = update.model_dump(exclude_unset=True)
        resp = await self._client.patch(
            f"{self._repo_path}/issues/{issue_number}", json=payload
        )
        resp.raise_for_status()
        return self._parse_issue(resp.json())

    @trace
    async def list_issue_comments(
        self, issue_number: int, per_page: int = 30, page: int = 1
    ) -> list[GitHubComment]:
        """List comments on an issue."""
        params: dict[str, int] = {"per_page": per_page, "page": page}
        resp = await self._client.get(
            f"{self._repo_path}/issues/{issue_number}/comments", params=params
        )
        resp.raise_for_status()
        return [self._parse_comment(c) for c in resp.json()]

    # ── Pull Requests ──────────────────────────────────────────────

    @trace
    async def list_pull_requests(
        self,
        state: str = "open",
        per_page: int = 30,
        page: int = 1,
    ) -> list[GitHubPullRequest]:
        """List pull requests."""
        params: dict[str, str | int] = {
            "state": state,
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "direction": "desc",
        }
        resp = await self._client.get(f"{self._repo_path}/pulls", params=params)
        resp.raise_for_status()
        return [self._parse_pull_request(pr) for pr in resp.json()]

    # ── Milestones ─────────────────────────────────────────────────

    @trace
    async def list_milestones(
        self, state: str = "open", per_page: int = 30, page: int = 1
    ) -> list[GitHubMilestone]:
        """List milestones."""
        params: dict[str, str | int] = {
            "state": state,
            "per_page": per_page,
            "page": page,
        }
        resp = await self._client.get(f"{self._repo_path}/milestones", params=params)
        resp.raise_for_status()
        return [self._parse_milestone(m) for m in resp.json()]

    # ── Labels ─────────────────────────────────────────────────────

    @trace
    async def list_labels(self, per_page: int = 100) -> list[GitHubLabel]:
        """List all repo labels."""
        resp = await self._client.get(
            f"{self._repo_path}/labels", params={"per_page": per_page}
        )
        resp.raise_for_status()
        return [
            GitHubLabel(
                name=lb["name"],
                color=lb.get("color", ""),
                description=lb.get("description"),
            )
            for lb in resp.json()
        ]

    # ── Contributors ───────────────────────────────────────────────

    @trace
    async def list_contributors(
        self, per_page: int = 30, page: int = 1
    ) -> list[GitHubUser]:
        """List repository contributors."""
        params: dict[str, int] = {"per_page": per_page, "page": page}
        resp = await self._client.get(
            f"{self._repo_path}/contributors", params=params
        )
        resp.raise_for_status()
        return [
            GitHubUser(
                login=u["login"],
                avatar_url=u.get("avatar_url", ""),
                html_url=u.get("html_url", ""),
            )
            for u in resp.json()
        ]

    # ── Parsing helpers ────────────────────────────────────────────

    @staticmethod
    def _parse_user(data: dict | None) -> GitHubUser | None:
        if not data:
            return None
        return GitHubUser(
            login=data["login"],
            avatar_url=data.get("avatar_url", ""),
            html_url=data.get("html_url", ""),
        )

    @staticmethod
    def _parse_label(data: dict) -> GitHubLabel:
        return GitHubLabel(
            name=data["name"],
            color=data.get("color", ""),
            description=data.get("description"),
        )

    @classmethod
    def _parse_milestone(cls, data: dict) -> GitHubMilestone:
        return GitHubMilestone(
            number=data["number"],
            title=data["title"],
            description=data.get("description"),
            state=data.get("state", "open"),
            open_issues=data.get("open_issues", 0),
            closed_issues=data.get("closed_issues", 0),
            due_on=data.get("due_on"),
            html_url=data.get("html_url", ""),
        )

    @classmethod
    def _parse_issue(cls, data: dict) -> GitHubIssue:
        milestone = None
        if data.get("milestone"):
            milestone = cls._parse_milestone(data["milestone"])

        pr_url: str | None = None
        if "pull_request" in data:
            pr_url = data["pull_request"].get("html_url")

        return GitHubIssue(
            number=data["number"],
            title=data["title"],
            body=data.get("body"),
            state=data.get("state", "open"),
            labels=[cls._parse_label(lb) for lb in data.get("labels", [])],
            assignees=[
                GitHubUser(
                    login=a["login"],
                    avatar_url=a.get("avatar_url", ""),
                    html_url=a.get("html_url", ""),
                )
                for a in data.get("assignees", [])
            ],
            user=cls._parse_user(data.get("user")),
            milestone=milestone,
            comments=data.get("comments", 0),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            closed_at=data.get("closed_at"),
            html_url=data.get("html_url", ""),
            pull_request_url=pr_url,
        )

    @classmethod
    def _parse_pull_request(cls, data: dict) -> GitHubPullRequest:
        return GitHubPullRequest(
            number=data["number"],
            title=data["title"],
            state=data.get("state", "open"),
            user=cls._parse_user(data.get("user")),
            labels=[cls._parse_label(lb) for lb in data.get("labels", [])],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            merged_at=data.get("merged_at"),
            html_url=data.get("html_url", ""),
            draft=data.get("draft", False),
        )

    @classmethod
    def _parse_comment(cls, data: dict) -> GitHubComment:
        return GitHubComment(
            id=data["id"],
            body=data.get("body", ""),
            user=cls._parse_user(data.get("user")),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            html_url=data.get("html_url", ""),
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()


# ── Dependency injection ──────────────────────────────────────────────

_project_service: ProjectService | None = None


def get_project_service() -> ProjectService:
    """Get the project service singleton.

    Reads owner/repo/token from settings. For production, consider
    using FastAPI Depends() with request-scoped services.
    """
    global _project_service
    if _project_service is None:
        from ...common.settings import get_settings

        settings = get_settings()
        owner, repo = settings.github_repo.split("/", 1)
        _project_service = ProjectService(
            owner=owner, repo=repo, token=settings.github_token
        )
    return _project_service
