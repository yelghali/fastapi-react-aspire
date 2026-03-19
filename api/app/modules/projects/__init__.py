"""Projects module - GitHub-integrated project management."""

from .routes import router as projects_router
from .schemas import (
    GitHubIssue,
    GitHubIssueCreate,
    GitHubLabel,
    GitHubMilestone,
    GitHubPullRequest,
    GitHubUser,
    RepoOverview,
)
from .service import ProjectService

__all__ = [
    "projects_router",
    "GitHubIssue",
    "GitHubIssueCreate",
    "GitHubLabel",
    "GitHubMilestone",
    "GitHubPullRequest",
    "GitHubUser",
    "ProjectService",
    "RepoOverview",
]
