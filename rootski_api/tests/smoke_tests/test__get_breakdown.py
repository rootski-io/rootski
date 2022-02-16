import asyncio
from asyncio import AbstractEventLoop
from random import randint
from typing import Coroutine, Final, List, Tuple

import httpx

# TODO: make this configurable so it can be used locally and against a production API instance
from httpx import Response

API_URL: Final[str] = "http://localhost:3333"


async def request_breakdown(word_id: int) -> (Response, int):
    """Do an async GET /breakdown request for a word_id.

    Returns:
        - the httpx.Response object from the async request
        - the word_id used to make the request
    """
    async with httpx.AsyncClient() as client:
        sleep_seconds = 1
        await asyncio.sleep(sleep_seconds)
        response: Response = await client.get(f"{API_URL}/breakdown/{word_id}")
        return response, word_id


def send_async__get_breakdown__requests_for_ids(word_ids: List[int]) -> List[Tuple[Response, int]]:
    """Do a GET /breakdown request for each word id in the argument

    Returns: List:
        - first item in a tuple is the httpx.Response object
        - second item is the word_id used to make the request
    """

    # run request_breakdown thousands of times and make sure all responses have code 404 or 200;
    # there is a "global" async event loop retrieved by asyncio.get_event_loop(); if we call .close()
    # on that loop... then we've closed the global event loop. We need to always get a new event loop
    # and set it as the global loop (I think)
    eloop: AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(eloop)
    coroutines: List[Coroutine[Response]] = [request_breakdown(word_id) for word_id in word_ids]
    responses: List[Tuple[Response, int]] = eloop.run_until_complete(asyncio.gather(*coroutines))
    eloop.close()
    return responses


def test__get_breakdown__return_only_200_and_404():
    """Run GET /breakdown for several batches of word ids and assert
    that they all return with status code 200 or 404."""

    num_requests_per_batch = 10
    num_batches = 5
    for i in range(num_batches):
        # request the breakdowns for a random batch of word_ids
        offset = i * randint(1, 1000)
        word_ids: List[int] = list(range(offset, offset + num_requests_per_batch))
        responses: List[Tuple[Response, int]] = send_async__get_breakdown__requests_for_ids(word_ids)

        # verify that only valid response codes were returned
        response: Response
        for response, word_id in responses:
            print("word_id", word_id)
            assert response.status_code in {200, 404}
