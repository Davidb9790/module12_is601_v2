import pytest
from unittest.mock import AsyncMock, patch

from app.auth.redis import get_redis, add_to_blacklist, is_blacklisted


@pytest.mark.asyncio
async def test_get_redis_initializes_and_caches():
    mock_client = AsyncMock()

    # Patch Redis.from_url so no real Redis is used
    with patch("app.auth.redis.redis.Redis.from_url", return_value=mock_client):
        # First call initializes
        client1 = await get_redis()
        # Second call returns cached instance
        client2 = await get_redis()

        assert client1 is client2


@pytest.mark.asyncio
async def test_add_to_blacklist_calls_set():
    mock_client = AsyncMock()

    # Patch get_redis to return our mock client
    with patch("app.auth.redis.get_redis", return_value=mock_client):
        await add_to_blacklist("abc123", 60)

        mock_client.set.assert_called_once_with("blacklist:abc123", "1", ex=60)


@pytest.mark.asyncio
async def test_is_blacklisted_calls_exists():
    mock_client = AsyncMock()
    mock_client.exists.return_value = True

    with patch("app.auth.redis.get_redis", return_value=mock_client):
        result = await is_blacklisted("xyz789")

        mock_client.exists.assert_called_once_with("blacklist:xyz789")
        assert result is True
