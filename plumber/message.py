"""
This module implement parsing and representation of a plumb message 
according to the format described in plan 9 plumb documentation
(see https://9fans.github.io/plan9port/man/man7/plumb.html)
"""
import typing
import construct

header_line = construct.NullTerminated(
    construct.GreedyString("utf-8"),
    term=b"\n"
)

def decode_attrs(raw: str) -> dict:
    import shlex
    pairs = shlex.split(raw)
    attrs = dict(
        p.split("=", maxsplit=1)
        for p in pairs
    )
    return attrs


def encode_attrs(attrs: dict) -> str:
    return " ".join(f"{k}=\"{str(v)}\"" for k, v in attrs.items())


PlumbMessageFormat = construct.Struct(
    "src" / header_line,
    "dst" / header_line,
    "type" / header_line,
    "attrs" / header_line,
    "ndata" / construct.Rebuild(
        header_line,
        lambda this: str(len(this.data))
    ),
    "data" / construct.Byte[lambda this: int(this.ndata)]
)


class PlumbMsg(typing.NamedTuple):
    src: str
    dst: str
    type: str
    attrs: dict
    ndata: int
    data: bytes

    
class ParseError(ValueError):
    pass
    

def decode(msg: bytes) -> PlumbMsg:
    msg = PlumbMessageFormat.parse(msg)
    
    return PlumbMsg(
        src=msg.src,
        dst=msg.dst,
        type=msg.type,
        attrs=decode_attrs(msg.attrs),
        ndata=int(msg.ndata),
        data=bytes(msg.data)
    )


def encode(msg: PlumbMsg) -> bytes:
    fields = dict(
        src=msg.src,
        dst=msg.dst,
        type=msg.type,
        attrs=encode_attrs(msg.attrs),
        ndata=str(msg.ndata),
        data=msg.data
    )
    return PlumbMessageFormat.build(fields)
