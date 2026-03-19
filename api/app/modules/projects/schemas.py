"""Pydantic schemas for the Projects module (GitHub integration)."""

from datetime import datetime

from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    """GitHub user summary."""

    login: str
    avatar_url: str = ""
    html_url: str = ""


class GitHubLabel(BaseModel):
    """GitHub issue/PR label."""

    name: str
    color: str = ""
    description: str | None = None


class GitHubMilestone(BaseModel):
    """GitHub milestone."""

    number: int
    title: str
    description: str | None = None
    state: str = "open"
    open_issues: int = 0
    closed_issues: int = 0
    due_on: datetime | None = None
    html_url: str = ""


class GitHubIssue(BaseModel):
    """GitHub issue."""

    number: int
    title: str
    body: str | None = None
    state: str = "open"
    labels: list[GitHubLabel] = Field(default_factory=list)
    assignees: list[GitHubUser] = Field(default_factory=list)
    user: GitHubUser | None = None
    milestone: GitHubMilestone | None = None
    comments: int = 0
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    html_url: str = ""
    pull_request_url: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "number": 1,
                    "title": "Add new feature",
                    "body": "Description of the feature",
                    "state": "open",
                    "labels": [{"name": "enhancement", "color": "a2eeef"}],
                    "assignees": [],
                    "comments": 2,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-02T00:00:00Z",
                    "html_url": "https://github.com/owner/repo/issues/1",
                }
            ]
        }
    }


class GitHubIssueCreate(BaseModel):
    """Schema for creating a new GitHub issue."""

    title: str = Field(..., min_length=1, max_length=256, description="Issue title")
    body: str = Field(default="", max_length=65536, description="Issue body (markdown)")
    labels: list[str] = Field(default_factory=list, description="Label names to apply")
    assignees: list[str] = Field(default_factory=list, description="Usernames to assign")
    milestone: int | None = Field(default=None, description="Milestone number")


class GitHubIssueUpdate(BaseModel):
    """Schema for updating a GitHub issue."""

    title: str | None = Field(default=None, min_length=1, max_length=256)
    body: str | None = Field(default=None, max_length=65536)
    state: str | None = Field(default=None, pattern="^(open|closed)$")
    labels: list[str] | None = Field(default=None)
    assignees: list[str] | None = Field(default=None)
    milestone: int | None = Field(default=None)


class GitHubPullRequest(BaseModel):
    """GitHub pull request summary."""

    number: int
    title: str
    state: str = "open"
    user: GitHubUser | None = None
    labels: list[GitHubLabel] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    merged_at: datetime | None = None
    html_url: str = ""
    draft: bool = False


class GitHubComment(BaseModel):
    """GitHub issue comment."""

    id: int
    body: str
    user: GitHubUser | None = None
    created_at: datetime
    updated_at: datetime
    html_url: str = ""


class RepoOverview(BaseModel):
    """Repository overview with stats."""

    full_name: str
    description: str | None = None
    html_url: str = ""
    stars: int = 0
    forks: int = 0
    open_issues_count: int = 0
    language: str | None = None
    topics: list[str] = Field(default_factory=list)
    default_branch: str = "main"
    updated_at: datetime | None = None
