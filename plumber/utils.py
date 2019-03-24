import trio
import trio.abc
from typing import Iterator


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


def multiplex_stream(stream: trio.abc.ReceiveStream, n: int, nursery):
    """
    Given a ReceiveStream, create multiplexed versions 
    that each receive all bytes sent to the original stream.
    """
    streams = []
    channels = []
    for i in range(n):
        send, receive = trio.open_memory_channel(1)
        streams.append((send, MultiplexedReceiveStream(receive)))
        
    async def multiplexer():
        while True:
            try:
                x = await stream.receive_some(1)
            except ...: # TODO: handle exceptions
                pass
            else:
                for send, _ in streams:
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
async def iterlines(stream: trio.abc.ReceiveStream) -> Iterator[str]:
    """yield lines from byte stream"""
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
        
