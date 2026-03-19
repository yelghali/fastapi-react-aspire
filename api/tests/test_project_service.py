"""Unit tests for the Projects service."""

from unittest.mock import AsyncMock

import pytest

from app.modules.projects.schemas import (
    GitHubIssueCreate,
    GitHubIssueUpdate,
)
from app.modules.projects.service import ProjectService


class MockResponse:
    """Minimal httpx-like response used for service unit tests."""

    def __init__(self, json_data):
        self._json_data = json_data

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._json_data


@pytest.fixture
def service() -> ProjectService:
    """Create a project service with a mocked HTTP client."""
    return ProjectService(owner="sethjuarez", repo="fastapi-react-aspire")


@pytest.mark.asyncio
async def test_repo_path(service: ProjectService):
    """Repository path should be composed from owner and repo."""
    assert service._repo_path == "/repos/sethjuarez/fastapi-react-aspire"


def test_token_header_is_set_when_token_is_provided():
    """Auth headers should include a bearer token when configured."""
    service = ProjectService(owner="owner", repo="repo", token="secret-token")

    assert service._client.headers["Authorization"] == "Bearer secret-token"


@pytest.mark.asyncio
async def test_list_issues_skips_pull_requests(service: ProjectService):
    """GitHub PR entries returned by /issues should be filtered out."""
    payload = [
        {
            "number": 1,
            "title": "Real issue",
            "state": "open",
            "labels": [],
            "assignees": [],
            "user": None,
            "milestone": None,
            "comments": 0,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
            "closed_at": None,
            "html_url": "https://example.com/issues/1",
        },
        {
            "number": 2,
            "title": "PR disguised as issue",
            "state": "open",
            "labels": [],
            "assignees": [],
            "user": None,
            "milestone": None,
            "comments": 0,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-02T00:00:00Z",
            "closed_at": None,
            "html_url": "https://example.com/issues/2",
            "pull_request": {"html_url": "https://example.com/pull/2"},
        },
    ]

    service._client.get = AsyncMock(return_value=MockResponse(payload))

    result = await service.list_issues(state="closed", labels="bug", per_page=10, page=2)

    assert len(result) == 1
    assert result[0].number == 1
    service._client.get.assert_awaited_once()
    _, kwargs = service._client.get.await_args
    assert kwargs["params"] == {
        "state": "closed",
        "per_page": 10,
        "page": 2,
        "sort": "updated",
        "direction": "desc",
        "labels": "bug",
    }


@pytest.mark.asyncio
async def test_create_issue_sends_only_populated_fields(service: ProjectService):
    """Issue creation payload should omit empty optional fields."""
    service._client.post = AsyncMock(
        return_value=MockResponse(
            {
                "number": 42,
                "title": "New issue",
                "body": "Body",
                "state": "open",
                "labels": [],
                "assignees": [],
                "user": None,
                "milestone": None,
                "comments": 0,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
                "closed_at": None,
                "html_url": "https://example.com/issues/42",
            }
        )
    )

    issue = GitHubIssueCreate(title="New issue", body="Body")
    result = await service.create_issue(issue)

    assert result.number == 42
    _, kwargs = service._client.post.await_args
    assert kwargs["json"] == {"title": "New issue", "body": "Body"}


@pytest.mark.asyncio
async def test_update_issue_sends_partial_payload(service: ProjectService):
    """Issue updates should send only provided fields."""
    service._client.patch = AsyncMock(
        return_value=MockResponse(
            {
                "number": 1,
                "title": "Updated",
                "state": "closed",
                "labels": [],
                "assignees": [],
                "user": None,
                "milestone": None,
                "comments": 0,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z",
                "closed_at": "2025-01-02T00:00:00Z",
                "html_url": "https://example.com/issues/1",
            }
        )
    )

    update = GitHubIssueUpdate(title="Updated", state="closed")
    result = await service.update_issue(1, update)

    assert result.state == "closed"
    _, kwargs = service._client.patch.await_args
    assert kwargs["json"] == {"title": "Updated", "state": "closed"}


@pytest.mark.asyncio
async def test_list_labels_parses_basic_fields(service: ProjectService):
    """Label responses should be converted into schema objects."""
    service._client.get = AsyncMock(
        return_value=MockResponse(
            [
                {"name": "bug", "color": "d73a4a", "description": "Bug report"},
                {"name": "enhancement", "color": "a2eeef"},
            ]
        )
    )

    result = await service.list_labels()

    assert [label.name for label in result] == ["bug", "enhancement"]
