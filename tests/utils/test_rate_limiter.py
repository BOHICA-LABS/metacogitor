import pytest
from metacogitor.utils import RateLimiter
import time
import asyncio


@pytest.fixture
async def rate_limiter():
    return RateLimiter(rpm=10)


@pytest.mark.asyncio
async def test_init(rate_limiter):
    rate_limiter = await rate_limiter
    assert rate_limiter.rpm == 10
    assert rate_limiter.interval == 6.6


@pytest.mark.asyncio
async def test_split_batches(rate_limiter):
    rate_limiter = await rate_limiter
    batch = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    batches = rate_limiter.split_batches(batch)
    assert len(batches) == 1
    assert batches[0] == batch

    batch = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    batches = rate_limiter.split_batches(batch)
    assert len(batches) == 2
    assert batches[0] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert batches[1] == [11, 12]


@pytest.mark.asyncio
async def test_wait_if_needed(rate_limiter):
    rate_limiter = await rate_limiter
    start_time = time.time()
    await rate_limiter.wait_if_needed(1)
    end_time = time.time()
    elapsed = end_time - start_time
    assert elapsed < rate_limiter.interval

    start_time = time.time()
    await rate_limiter.wait_if_needed(2)
    end_time = time.time()
    elapsed = end_time - start_time
    assert elapsed >= rate_limiter.interval
