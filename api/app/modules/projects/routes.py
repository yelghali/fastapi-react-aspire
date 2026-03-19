"""API routes for the Projects module (GitHub project management)."""

from fastapi import APIRouter, Depends, HTTPException, Query

from ...common.tracer import trace_span
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
from .service import ProjectService, get_project_service

router = APIRouter(prefix="/projects", tags=["projects"])


# ── Repo overview ──────────────────────────────────────────────────


@router.get(
    "/overview",
    response_model=RepoOverview,
    summary="Get repository overview",
    description="Retrieve repository metadata including stars, forks, and open issues count.",
)
async def get_overview(
    service: ProjectService = Depends(get_project_service),
) -> RepoOverview:
    with trace_span("get_repo_overview"):
        return await service.get_repo_overview()


# ── Issues ─────────────────────────────────────────────────────────


@router.get(
    "/issues",
    response_model=list[GitHubIssue],
    summary="List issues",
    description="List repository issues with optional filters. Excludes pull requests.",
)
async def list_issues(
    state: str = Query(default="open", pattern="^(open|closed|all)$"),
    labels: str = Query(default="", description="Comma-separated label names"),
    assignee: str = Query(default="", description="Filter by assignee username"),
    milestone: str = Query(default="", description="Milestone number or 'none'/'*'"),
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    service: ProjectService = Depends(get_project_service),
) -> list[GitHubIssue]:
    with trace_span("list_issues", attributes={"state": state, "page": page}):
        return await service.list_issues(
            state=state,
            labels=labels,
            assignee=assignee,
            milestone=milestone,
            per_page=per_page,
            page=page,
        )


@router.get(
    "/issues/{issue_number}",
    response_model=GitHubIssue,
    summary="Get an issue",
    description="Retrieve a single issue by its number.",
)
async def get_issue(
    issue_number: int,
    service: ProjectService = Depends(get_project_service),
) -> GitHubIssue:
    with trace_span("get_issue", attributes={"issue_number": issue_number}):
        try:
            return await service.get_issue(issue_number)
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/issues",
    response_model=GitHubIssue,
    status_code=201,
    summary="Create an issue",
    description="Create a new issue. Requires a configured GitHub token with repo scope.",
)
async def create_issue(
    issue: GitHubIssueCreate,
    service: ProjectService = Depends(get_project_service),
) -> GitHubIssue:
    with trace_span("create_issue", attributes={"title": issue.title}):
        try:
            return await service.create_issue(issue)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.patch(
    "/issues/{issue_number}",
    response_model=GitHubIssue,
    summary="Update an issue",
    description="Update an existing issue. Requires a configured GitHub token with repo scope.",
)
async def update_issue(
    issue_number: int,
    update: GitHubIssueUpdate,
    service: ProjectService = Depends(get_project_service),
) -> GitHubIssue:
    with trace_span("update_issue", attributes={"issue_number": issue_number}):
        try:
            return await service.update_issue(issue_number, update)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get(
    "/issues/{issue_number}/comments",
    response_model=list[GitHubComment],
    summary="List issue comments",
    description="List comments on a specific issue.",
)
async def list_issue_comments(
    issue_number: int,
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    service: ProjectService = Depends(get_project_service),
) -> list[GitHubComment]:
    with trace_span("list_issue_comments", attributes={"issue_number": issue_number}):
        return await service.list_issue_comments(
            issue_number, per_page=per_page, page=page
        )


# ── Pull Requests ──────────────────────────────────────────────────


@router.get(
    "/pulls",
    response_model=list[GitHubPullRequest],
    summary="List pull requests",
    description="List repository pull requests.",
)
async def list_pull_requests(
    state: str = Query(default="open", pattern="^(open|closed|all)$"),
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    service: ProjectService = Depends(get_project_service),
) -> list[GitHubPullRequest]:
    with trace_span("list_pull_requests", attributes={"state": state}):
        return await service.list_pull_requests(
            state=state, per_page=per_page, page=page
        )


# ── Milestones ─────────────────────────────────────────────────────


@router.get(
    "/milestones",
    response_model=list[GitHubMilestone],
    summary="List milestones",
    description="List repository milestones.",
)
async def list_milestones(
    state: str = Query(default="open", pattern="^(open|closed|all)$"),
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    service: ProjectService = Depends(get_project_service),
) -> list[GitHubMilestone]:
    with trace_span("list_milestones", attributes={"state": state}):
        return await service.list_milestones(state=state, per_page=per_page, page=page)


# ── Labels ─────────────────────────────────────────────────────────


@router.get(
    "/labels",
    response_model=list[GitHubLabel],
    summary="List labels",
    description="List all repository labels.",
)
async def list_labels(
    service: ProjectService = Depends(get_project_service),
) -> list[GitHubLabel]:
    with trace_span("list_labels"):
        return await service.list_labels()


# ── Contributors ───────────────────────────────────────────────────


@router.get(
    "/contributors",
    response_model=list[GitHubUser],
    summary="List contributors",
    description="List repository contributors.",
)
async def list_contributors(
    per_page: int = Query(default=30, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    service: ProjectService = Depends(get_project_service),
) -> list[GitHubUser]:
    with trace_span("list_contributors"):
        return await service.list_contributors(per_page=per_page, page=page)
