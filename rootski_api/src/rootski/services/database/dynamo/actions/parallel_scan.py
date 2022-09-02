"""DynamoDB parallel scan paginator for boto3.

Adapted from parallel scan implementation of Alex Chan (MIT license):
https://alexwlchan.net/2020/05/getting-every-item-from-a-dynamodb-table-with-python/

Then adapted from Sami Jaktholm
https://github.com/sjakthol/python-aws-dynamodb-parallel-scan/blob/main/aws_dynamodb_parallel_scan.py
"""


import concurrent.futures
import typing

if typing.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_dynamodb import DynamoDBClient
else:
    DynamoDBClient = None  # pylint: disable=invalid-name


class Paginator:  # pylint: disable=too-few-public-methods
    """Paginator that implements DynamoDB parallel scan.
    Similar to boto3 DynamoDB scan paginator but scans the table in
    parallel.
    """

    def __init__(self, client: DynamoDBClient):
        """Create paginator for DynamoDB parallel scan.
        Args:
            client: DynamoDB client to use for Scan API calls.
        """
        self._client = client

    def paginate(self, **kwargs):
        # pylint: disable=line-too-long
        """Creates a generator that yields DynamoDB Scan API responses.
        paginate() accepts the same arguments as boto3 DynamoDB.Client.scan() method. Arguments
        are passed to DynamoDB.Client.scan() as-is.
        paginate() uses the value of TotalSegments argument as parallelism level. Each segment
        is scanned in parallel in a separate thread.
        paginate() yields DynamoDB Scan API responses boto3 DynamoDB.Paginator.Scan.paginate()
        method.
        See boto3 DynamoDB.Client.scan documentation (https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.scan)
        for details on supported arguments and the response format.
        """
        # pylint: enable=line-too-long
        segments = kwargs.get("TotalSegments") or 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=segments) as executor:

            # Prepare Scan arguments for each segment of the parallel scan.
            tasks = ({**kwargs, "TotalSegments": segments, "Segment": i} for i in range(segments))

            # Submit scan operation for each segment
            futures = {executor.submit(self._client.scan, **t): t for t in tasks}

            while futures:
                # Collect results
                done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)

                for future in done:
                    # Get the result and the scan args for the completed operation
                    task = futures.pop(future)
                    page = future.result()
                    yield page

                    next_key = page.get("LastEvaluatedKey")
                    if next_key:
                        # Still more items in this segment. Submit another scan operation for this
                        # segment that continues where the last one left off.
                        futures[
                            executor.submit(self._client.scan, **{**task, "ExclusiveStartKey": next_key})
                        ] = task


def get_paginator(client: DynamoDBClient):
    """Create paginator for DynamoDB parallel scan.
    Args:
        client: DynamoDB client to use for Scan API calls.
    Returns: Paginator object.
    """
    return Paginator(client)
