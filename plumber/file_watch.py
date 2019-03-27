"""
This module implement asynchronous file watching utilities
"""
import trio
import time


async def poll_change(path: trio.Path, poll_frequency=1):
    """
    Create an synchronous generator over changes on a file,
    implemented by polling for recent modifications using stats system call 
    """
    last_modified = time.time_ns()
    while True:
        stats = await path.stats()
        if stats.st_mtime_ns > last_modified:
            last_modified = stats.st_mtime_ns
            # TODO: yield something useful
            yield stats
        await trio.sleep(poll_frequency)



async def poll_diff(path: trio.Path, poll_frequency=1):
    """
    Poll file for changes and yield diffs.
    """
    raise NotImplementedError
