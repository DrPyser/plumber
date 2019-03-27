"""
This module implement command execution using trio.
commands are programs that are executed in subprocesses
and receive a plumb message through their standard input.
"""
import trio
import subprocess
from plumber.message import PlumbMsg
from plumber.utils import iterlines
import typing
import json
import functools
import logging
           

class Command(typing.NamedTuple):
    command: str
    """A command string"""
    interpreter: typing.List[str]
    """An interpreter program exec array"""

    
async def log_output(logger, stream, task_status=trio.TASK_STATUS_IGNORED):
    async with stream:
        task_status.started()
        async for l in iterlines(stream):
            logger.debug(l)

            
def json_serialize(msg: PlumbMsg):
    # TODO: allow different encoding for data
    return json.dumps(dict(
        src=msg.src,
        dst=msg.dst,
        type=msg.type,
        attrs=msg.attrs,
        data=msg.data.decode("utf-8")
    )).encode("utf-8")
    

async def read_output(stream, chunk_size):
    async with stream:
        while True:
            chunk = await stream.receive_some(chunk_size)
            if not chunk:
                break
            else:
                yield chunk

                
async def feed_input(stream, input_data):
    async with stream:
        if input_data:
            try:
                await stream.send_all(input_data)
            except trio.BrokenResourceError as ex:
                raise

            
class Executor:
    """Execute a command in a subprocess, with a plumb message passed through its standard input"""
    #__slots__ = [""]
    def __init__(self, serializer, stdout_handler, stderr_handler, logger):
        self.serializer = serializer
        self.stdout_handler = stdout_handler
        self.stderr_handler = stderr_handler
        self.logger = logger
        
    async def __call__(self, command: Command, msg: PlumbMsg):
        process_command = [*command.interpreter, *command.command]
        async with trio.Process(process_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            print("opened process {!r}".format(process_command))
            async with trio.open_nursery() as nursery:
                input_data = self.serializer(msg) + b"\n"
                self.logger.debug("input=%s", input_data)
                nursery.start_soon(feed_input, proc.stdin, input_data)
                # TODO: havef handlers return BytesIO or StringIO on start and write to it
                stdout_capture = await nursery.start(self.stdout_handler, proc.stdout)                
                stderr_capture = await nursery.start(self.stderr_handler, proc.stderr)
                await proc.wait()

            if proc.returncode:
                raise subprocess.CalledProcessError(
                    proc.returncode, proc.args,
                    output=stdout_capture,
                    stderr=stderr_capture
                )
            else:
                return subprocess.CompletedProcess(
                    proc.args, proc.returncode,
                    stdout_capture,
                    stderr_capture
                )


logger = logging.getLogger(__name__)
executor = Executor(json_serialize, functools.partial(log_output, logger), functools.partial(log_output, logger), logger=logger)


def main():
    logging.basicConfig(level=logging.DEBUG)
    msg = PlumbMsg(src="", dst="", type="text", attrs=dict(x=1), data=b"Hello World!")
    command = Command(command=["jq .data"], interpreter=["sh", "-c"])
    trio.run(executor, command, msg)

    
