import typing
import enum


class PlumbMsg(typing.NamedTuple):
    src: str
    dst: str
    type: str
    attrs: dict
    data: bytes

    
# TODO: add json parser
# TODO: add msgpack parser
# TODO: add plan9 plumber parser (https://9fans.github.io/plan9port/man/man7/plumb.html)


# class Rule(typing.NamedTuple):
    


# RuleCollection = typing.Dict[str, ]
