"""
This module implement parsing and representation of a plumb message 
according to the format described in plan 9 plumb documentation
(see https://9fans.github.io/plan9port/man/man7/plumb.html)
"""
import typing


class PlumbMsg(typing.NamedTuple):
    src: str
    dst: str
    type: str
    attrs: dict
    ndata: int
    data: bytes

    def __str__(self):
        head = "{}\n{}\n{}\n{}\n{}\n".format(
            self.src,
            self.dst,
            self.type,
            " ".join(
                k+"="+v
                for k,v in self.attrs.items()
            ),
            self.ndata
        )
        return head.encode("utf-8") + self.data

    
class ParseError(ValueError):
    pass
    

def parse_message(msg: bytes) -> PlumbMsg:
    fields = msg.split(b"\n", maxsplit=5)
    if len(fields) != 6:
        raise ParseError
    raw_src, raw_dst, raw_mtype, raw_attrs, raw_ndata, raw_data = fields
    src = raw_src.decode("utf-8")
    dst = raw_dst.decode("utf-8")
    mtype = raw_mtype.decode("utf-8")
    # TODO: fix this to support whitespace in quoted values
    attrs_pairs = raw_attrs.decode("utf-8").split()
    # TODO: values can be in quotes, and should be parsed accordingly("evaluated")
    attrs = dict(
        (k, v)
        for k, v in (
            p.split("=", maxsplit=1)
            for p in attrs_pairs
        )
    )
    ndata = int(raw_ndata.decode("utf-8")) if len(raw_ndata) != 0 else None
    data = raw_data # data is kept as raw bytes
    if ndata is not None and len(data) != ndata:
        raise ParseError
    
    return PlumbMsg(
        src=src,
        dst=dst,
        type=mtype,
        attrs=attrs,
        ndata=ndata,
        data=data
    )

