"""Rate limiter module for the Metacogitor API client."""
# -*- coding: utf-8 -*-


import asyncio
import time
from metacogitor.logs import logger  # Import the logger module if not already done


class RateLimiter:
    """
    Rate control class that enforces a limit on the rate of API calls.
    Each call goes through wait_if_needed, and sleeps if rate control is needed.
    """

    def __init__(self, rpm):
        """
        Initialize the RateLimiter instance.

        :param rpm: Requests per minute to limit the rate.
        """
        self.last_call_time = 0
        # Using 1.1 for interval calculation to account for QoS even with strict time adherence
        self.interval = 1.1 * 60 / rpm
        self.rpm = rpm

    def split_batches(self, batch):
        """
        Split a batch into sub-batches of the specified size.

        :param batch: List to be split into sub-batches.
        :return: List of sub-batches.
        """
        return [batch[i : i + self.rpm] for i in range(0, len(batch), self.rpm)]

    async def wait_if_needed(self, num_requests):
        """
        Asynchronously wait if the rate limit needs to be enforced.

        :param num_requests: Number of requests made.
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_call_time

        if elapsed_time < self.interval * num_requests:
            remaining_time = self.interval * num_requests - elapsed_time
            logger.info(f"Sleeping for {remaining_time} seconds")
            await asyncio.sleep(remaining_time)

        self.last_call_time = time.time()
