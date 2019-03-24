import trio
import subprocess
from plumber.common import PlumbMsg
import typing
import json
import functools
import logging
           

class Command(typing.NamedTuple):
    command: str
    """A command string"""
    interpreter: typing.List[str]
    """An interpreter program exec array"""

# TODO: move to utils module    
async def anext(it):
    return await it.__anext__()

# TODO: move to utils module    
async def take(ait, n: int):
    for i in n:
        try:
            yield await anext(it)
        except StopAsyncIteration:
            return
        
# TODO: move to utils module    
class MultiplexedReceiveStream(trio.abc.ReceiveStream):
    def __init__(self, channel: trio.abc.ReceiveChannel):
        self.channel = channel

    async def receive_some(self, max_bytes):
        some = [b async for b in take(self.channel, max_bytes)]
        return bytearray(some)

# TODO: move to utils module        
def multiplex_stream(stream: trio.abc.ReceiveStream, n: int, nursery):
    streams = []
    channels = []
    for i in range(n):
        send, receive = trio.open_memory_channel()
        streams.append((send, MultiplexedReceiveStream(receive)))
    async def multiplexer():
        async for x in stream:
            for send, s in streams:
                await send.send(x)
    nursery.start_soon(multiplexer)
    return [s for _, s in streams]

# TODO: move to utils module    
async def multiplex(stream, readers):
    readers = list(readers)
    async with trio.open_nursery() as nursery:
        multiplexed = multiplex_stream(stream, len(readers), nursery)
        for r, s in zip(readers, multiplexed):
            nursery.start_soon(r, r(s))

# TODO: move to utils module    
async def iterlines(stream):
    bs = ""
    while True:
        try:
            b = await stream.receive_some(1)
        except trio.ClosedResourceError:
            return
        except trio.BusyResourceError:
            pass
        else:
            if len(b) == 0:
                return
            else:
                text = b.decode("utf-8")
                bs += text
                if text == "\n":
                    yield bs
                    bs = ""

                    
async def log_output(logger, stream, task_status=trio.TASK_STATUS_IGNORED):
    async with stream:
        task_status.started()
        async for l in iterlines(stream):
            logger.debug(l)

def json_serialize(msg: PlumbMsg):
    return json.dumps(dict(
        src=msg.src,
        dst=msg.dst,
        type=msg.type,
        attrs=msg.attrs,
        data=msg.data.hex()
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

    
