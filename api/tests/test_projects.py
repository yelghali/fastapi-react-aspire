"""Tests for the Projects module."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# Sample GitHub API response payloads
SAMPLE_REPO = {
    "full_name": "sethjuarez/fastapi-react-aspire",
    "description": "A starter template",
    "html_url": "https://github.com/sethjuarez/fastapi-react-aspire",
    "stargazers_count": 42,
    "forks_count": 5,
    "open_issues_count": 3,
    "language": "Python",
    "topics": ["fastapi", "react"],
    "default_branch": "main",
    "updated_at": "2025-06-01T00:00:00Z",
}

SAMPLE_ISSUE = {
    "number": 1,
    "title": "Fix README typo",
    "body": "There is a typo in the README",
    "state": "open",
    "labels": [{"name": "bug", "color": "d73a4a", "description": "Bug report"}],
    "assignees": [
        {"login": "alice", "avatar_url": "https://example.com/a.png", "html_url": ""}
    ],
    "user": {"login": "bob", "avatar_url": "https://example.com/b.png", "html_url": ""},
    "milestone": None,
    "comments": 2,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-02T00:00:00Z",
    "closed_at": None,
    "html_url": "https://github.com/sethjuarez/fastapi-react-aspire/issues/1",
}

SAMPLE_PR = {
    "number": 10,
    "title": "Add projects module",
    "state": "open",
    "user": {"login": "dev", "avatar_url": "", "html_url": ""},
    "labels": [],
    "created_at": "2025-06-01T00:00:00Z",
    "updated_at": "2025-06-02T00:00:00Z",
    "merged_at": None,
    "html_url": "https://github.com/sethjuarez/fastapi-react-aspire/pull/10",
    "draft": False,
}

SAMPLE_MILESTONE = {
    "number": 1,
    "title": "v1.0",
    "description": "First release",
    "state": "open",
    "open_issues": 3,
    "closed_issues": 7,
    "due_on": "2025-12-31T00:00:00Z",
    "html_url": "https://github.com/sethjuarez/fastapi-react-aspire/milestone/1",
}

SAMPLE_LABEL = {"name": "bug", "color": "d73a4a", "description": "Bug report"}

SAMPLE_CONTRIBUTOR = {
    "login": "contributor1",
    "avatar_url": "https://example.com/c.png",
    "html_url": "https://github.com/contributor1",
}

SAMPLE_COMMENT = {
    "id": 100,
    "body": "Looks good!",
    "user": {"login": "reviewer", "avatar_url": "", "html_url": ""},
    "created_at": "2025-01-03T00:00:00Z",
    "updated_at": "2025-01-03T00:00:00Z",
    "html_url": "https://github.com/sethjuarez/fastapi-react-aspire/issues/1#issuecomment-100",
}


def _mock_response(json_data, status_code=200):
    """Create a mock httpx response."""
    mock = AsyncMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    mock.raise_for_status = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_get_overview(client: AsyncClient):
    """Test getting repo overview."""
    with patch(
        "app.modules.projects.service.ProjectService.get_repo_overview"
    ) as mock:
        from app.modules.projects.schemas import RepoOverview

        mock.return_value = RepoOverview(
            full_name="sethjuarez/fastapi-react-aspire",
            description="A starter template",
            html_url="https://github.com/sethjuarez/fastapi-react-aspire",
            stars=42,
            forks=5,
            open_issues_count=3,
            language="Python",
            topics=["fastapi", "react"],
            default_branch="main",
            updated_at="2025-06-01T00:00:00Z",
        )
        response = await client.get("/api/projects/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "sethjuarez/fastapi-react-aspire"
        assert data["stars"] == 42


@pytest.mark.asyncio
async def test_list_issues(client: AsyncClient):
    """Test listing issues."""
    with patch(
        "app.modules.projects.service.ProjectService.list_issues"
    ) as mock:
        from app.modules.projects.schemas import GitHubIssue

        mock.return_value = [
            GitHubIssue(
                number=1,
                title="Fix README typo",
                state="open",
                comments=2,
                created_at="2025-01-01T00:00:00Z",
                updated_at="2025-01-02T00:00:00Z",
            )
        ]
        response = await client.get("/api/projects/issues")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["number"] == 1
        assert data[0]["title"] == "Fix README typo"


@pytest.mark.asyncio
async def test_list_issues_with_filters(client: AsyncClient):
    """Test listing issues with state filter."""
    with patch(
        "app.modules.projects.service.ProjectService.list_issues"
    ) as mock:
        mock.return_value = []
        response = await client.get("/api/projects/issues?state=closed&labels=bug")
        assert response.status_code == 200
        mock.assert_called_once_with(
            state="closed",
            labels="bug",
            assignee="",
            milestone="",
            per_page=30,
            page=1,
        )


@pytest.mark.asyncio
async def test_get_issue(client: AsyncClient):
    """Test getting a single issue."""
    with patch(
        "app.modules.projects.service.ProjectService.get_issue"
    ) as mock:
        from app.modules.projects.schemas import GitHubIssue

        mock.return_value = GitHubIssue(
            number=1,
            title="Fix README typo",
            body="There is a typo",
            state="open",
            comments=2,
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-02T00:00:00Z",
        )
        response = await client.get("/api/projects/issues/1")
        assert response.status_code == 200
        data = response.json()
        assert data["number"] == 1


@pytest.mark.asyncio
async def test_get_issue_not_found(client: AsyncClient):
    """Test getting a missing issue returns 404."""
    with patch(
        "app.modules.projects.service.ProjectService.get_issue"
    ) as mock:
        mock.side_effect = Exception("issue 404")

        response = await client.get("/api/projects/issues/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "issue 404"


@pytest.mark.asyncio
async def test_create_issue(client: AsyncClient):
    """Test creating an issue."""
    with patch(
        "app.modules.projects.service.ProjectService.create_issue"
    ) as mock:
        from app.modules.projects.schemas import GitHubIssue

        mock.return_value = GitHubIssue(
            number=42,
            title="New feature request",
            body="Please add this",
            state="open",
            comments=0,
            created_at="2025-06-01T00:00:00Z",
            updated_at="2025-06-01T00:00:00Z",
        )
        response = await client.post(
            "/api/projects/issues",
            json={"title": "New feature request", "body": "Please add this"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["number"] == 42
        assert data["title"] == "New feature request"


@pytest.mark.asyncio
async def test_create_issue_validation_error(client: AsyncClient):
    """Test that invalid issue payloads are rejected."""
    response = await client.post(
        "/api/projects/issues",
        json={"body": "Missing title"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_issue(client: AsyncClient):
    """Test updating an issue."""
    with patch(
        "app.modules.projects.service.ProjectService.update_issue"
    ) as mock:
        from app.modules.projects.schemas import GitHubIssue

        mock.return_value = GitHubIssue(
            number=1,
            title="Updated title",
            state="closed",
            comments=2,
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-06-01T00:00:00Z",
            closed_at="2025-06-01T00:00:00Z",
        )
        response = await client.patch(
            "/api/projects/issues/1",
            json={"title": "Updated title", "state": "closed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["state"] == "closed"


@pytest.mark.asyncio
async def test_update_issue_validation_error(client: AsyncClient):
    """Test that invalid update payloads are rejected."""
    response = await client.patch(
        "/api/projects/issues/1",
        json={"state": "invalid"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_issue_comments(client: AsyncClient):
    """Test listing issue comments."""
    with patch(
        "app.modules.projects.service.ProjectService.list_issue_comments"
    ) as mock:
        from app.modules.projects.schemas import GitHubComment

        mock.return_value = [
            GitHubComment(
                id=100,
                body="Looks good!",
                created_at="2025-01-03T00:00:00Z",
                updated_at="2025-01-03T00:00:00Z",
            )
        ]
        response = await client.get("/api/projects/issues/1/comments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["body"] == "Looks good!"


@pytest.mark.asyncio
async def test_list_issue_comments_with_pagination(client: AsyncClient):
    """Test pagination parameters are forwarded to the service."""
    with patch(
        "app.modules.projects.service.ProjectService.list_issue_comments"
    ) as mock:
        mock.return_value = []

        response = await client.get(
            "/api/projects/issues/1/comments?per_page=10&page=2"
        )

        assert response.status_code == 200
        mock.assert_called_once_with(1, per_page=10, page=2)


@pytest.mark.asyncio
async def test_list_pull_requests(client: AsyncClient):
    """Test listing pull requests."""
    with patch(
        "app.modules.projects.service.ProjectService.list_pull_requests"
    ) as mock:
        from app.modules.projects.schemas import GitHubPullRequest

        mock.return_value = [
            GitHubPullRequest(
                number=10,
                title="Add projects module",
                state="open",
                created_at="2025-06-01T00:00:00Z",
                updated_at="2025-06-02T00:00:00Z",
                draft=False,
            )
        ]
        response = await client.get("/api/projects/pulls")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["number"] == 10


@pytest.mark.asyncio
async def test_list_pull_requests_with_filters(client: AsyncClient):
    """Test pull request filters are forwarded to the service."""
    with patch(
        "app.modules.projects.service.ProjectService.list_pull_requests"
    ) as mock:
        mock.return_value = []

        response = await client.get("/api/projects/pulls?state=closed&per_page=5&page=3")

        assert response.status_code == 200
        mock.assert_called_once_with(state="closed", per_page=5, page=3)


@pytest.mark.asyncio
async def test_list_milestones(client: AsyncClient):
    """Test listing milestones."""
    with patch(
        "app.modules.projects.service.ProjectService.list_milestones"
    ) as mock:
        from app.modules.projects.schemas import GitHubMilestone

        mock.return_value = [
            GitHubMilestone(
                number=1,
                title="v1.0",
                state="open",
                open_issues=3,
                closed_issues=7,
            )
        ]
        response = await client.get("/api/projects/milestones")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "v1.0"


@pytest.mark.asyncio
async def test_list_labels(client: AsyncClient):
    """Test listing labels."""
    with patch(
        "app.modules.projects.service.ProjectService.list_labels"
    ) as mock:
        from app.modules.projects.schemas import GitHubLabel

        mock.return_value = [
            GitHubLabel(name="bug", color="d73a4a", description="Bug report")
        ]
        response = await client.get("/api/projects/labels")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "bug"


@pytest.mark.asyncio
async def test_list_contributors(client: AsyncClient):
    """Test listing contributors."""
    with patch(
        "app.modules.projects.service.ProjectService.list_contributors"
    ) as mock:
        from app.modules.projects.schemas import GitHubUser

        mock.return_value = [
            GitHubUser(
                login="contributor1",
                avatar_url="https://example.com/c.png",
                html_url="https://github.com/contributor1",
            )
        ]
        response = await client.get("/api/projects/contributors")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["login"] == "contributor1"
