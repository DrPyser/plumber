"""
This module implement parsers for each 9p message type
"""
import enum
import construct
# import typing


class MessageType(enum.Enum):
    Tversion = 100
    Rversion = 101
    Tauth = 102
    Rauth = 103
    Tattach = 104
    Rattach = 105
    Rerror = 107
    Tflush = 108
    Rflush = 109
    Twalk = 110
    Rwalk = 111
    Topen = 112
    Ropen = 113
    Tcreate = 114
    Rcreate = 115
    Tread = 116
    Rread = 117
    Twrite = 118
    Rwrite = 119
    Tclunk = 120
    Rclunk = 121
    Tremove = 122
    Rremove = 123
    Tstat = 124
    Rstat = 125
    Twstat = 126
    Rwstat = 127
    Topenfd = 128
    Ropenfd = 129

    
LengthPrefixField = construct.Int16ul # msize[2]
StringField = construct.PascalString(LengthPrefixField, "utf-8")
TagField = construct.Int16ul * "message identifier, unique throughout session"
SizeField = construct.Int32ul * "size of entired message including size field" # size is 32bit / 4 bytes
TypeField = construct.Bytes(1) * "message type" # type is 1 byte

FidField = construct.Int32ul * """A fid is an identifier for a pointer to a 9p file, akin to a file descriptor"""

QidField = construct.Struct(
    "qtype" / construct.Int8ul * "file type",
    "version" / construct.Int32ul * "file version",
    "path" / construct.Int64ul
) * """A qid is a unique identifier for a file on the serverside. No two file will ever share the same qid."""

ModeField = construct.Int8ul * "file mode(write, read, append, ...)"

# size[4] Tversion tag[2] msize[4] version[s]
Tversion = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tversion.value, TypeField),
    "tag" / TagField,
    "msize" / construct.Int32ul * "maximum message size",
    "version" / StringField * "protocol version"
)

# size[4] Rversion tag[2] msize[4] version[s]
Rversion = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rversion.value, TypeField),
    "tag" / TagField,
    "msize" / construct.Int32ul * "maximum message size",
    "version" / StringField * "protocol version"
)

# size[4] Tauth tag[2] afid[4] uname[s] aname[s]
Tauth = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tauth.value, TypeField),
    "tag" / TagField,
    "afid" / FidField,
    "uname" / StringField,
    "aname" / StringField
)

# size[4] Rauth tag[2] aqid[13]
Rauth = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rauth.value, TypeField),
    "tag" / TagField,
    "aqid" / construct.Embedded(
        QidField
    )
)

# size[4] Rerror tag[2] ename[s]
Rerror = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rerror.value, TypeField),
    "tag" / TagField,
    "ename" / StringField * "error name"
) * "error response"

# size[4] Tflush tag[2] oldtag[2]
Tflush = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tflush.value, TypeField),
    "tag" / TagField,
    "oldtag" / TagField
)

# size[4] Rflush tag[2]
Rflush = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rflush.value, TypeField),
    "tag" / TagField,
)

# size[4] Tattach tag[2] fid[4] afid[4] uname[s] aname[s]
Tattach = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tattach.value, TypeField),
    "tag" / TagField,
    "fid" / FidField,
    "afid" / FidField,
    "uname" / StringField,
    "aname" / StringField
)

# size[4] Rattach tag[2] qid[13]
Rattach = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rattach.value, TypeField),
    "tag" / TagField,
    "qid" / construct.Embedded(
        QidField
    )
)

# size[4] Twalk tag[2] fid[4] newfid[4] nwname[2] nwname*(wname[s])
Twalk = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Twalk.value, TypeField),
    "tag" / TagField,
    "fid" / FidField,
    "newfid" / FidField,
    "nwname" / construct.Int16ul,
    "wname" / StringField[construct.this.nwname]
)

# size[4] Rwalk tag[2] nwqid[2] nwqid*(wqid[13])
Rwalk = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rwalk.value, TypeField),
    "tag" / TagField,
    "nwqid" / construct.Int16ul,
    "wqid" / QidField[construct.this.nwqid] # TODO: embed each array element
)

# size[4] Topen tag[2] fid[4] mode[1]
Topen = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Topen.value, TypeField),
    "tag" / TagField,
    "fid" / FidField,
    "mode" / ModeField
)

IOUnitField = construct.Int32ul

# size[4] Ropen tag[2] qid[13] iounit[4]
Ropen = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Ropen.value, TypeField),
    "tag" / TagField,
    "qid" / construct.Embedded(
        QidField
    ),
    "iounit" / IOUnitField
)

# size[4] Topenfd tag[2] fid[4] mode[1]
Topenfd = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Topenfd.value, TypeField),
    "tag" / TagField,
    "fid" / FidField,
    "mode" / ModeField
)

# size[4] Ropenfd tag[2] qid[13] iounit[4] unixfd[4]
Ropenfd = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Ropenfd.value, TypeField),
    "tag" / TagField,
    "qid" / construct.Embedded(
        QidField
    ),
    "iounit" / IOUnitField,
    "unixfd" / construct.Int32ul
)

PermField = construct.Int32ul

# size[4] Tcreate tag[2] fid[4] name[s] perm[4] mode[1]
Tcreate = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tcreate.value, TypeField),
    "tag" / TagField,
    "fid" / FidField,
    "name" / StringField,
    "perm" / PermField,
    "mode" / ModeField
)

# size[4] Rcreate tag[2] qid[13] iounit[4]
Rcreate = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rcreate.value, TypeField),
    "tag" / TagField,
    "qid" / construct.Embedded(
        QidField
    ),
    "iounit" / IOUnitField
)

OffsetField = construct.Int64ul
CountField = construct.Int32ul

# size[4] Tread tag[2] fid[4] offset[8] count[4]
Tread = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tread.value, TypeField),
    "tag" / TagField,
    "fid" / FidField,
    "offset" / OffsetField,
    "count" / CountField
)

# size[4] Rread tag[2] count[4] data[count]
Rread = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rread.value, TypeField),
    "tag" / TagField,
    "count" / CountField,
    "data" / construct.Byte[construct.this.count]
)

# size[4] Twrite tag[2] fid[4] offset[8] count[4] data[count]
Twrite = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Twrite.value, TypeField),
    "tag" / TagField,
    "fid" / FidField,
    "offset" / OffsetField,
    "count" / CountField,
    "data" / construct.Byte[construct.this.count]
)

# size[4] Rwrite tag[2] count[4]
Rwrite = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rwrite.value, TypeField),
    "tag" / TagField,
    "count" / CountField
)

# size[4] Tclunk tag[2] fid[4]
Tclunk = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tclunk.value, TypeField),
    "tag" / TagField,
    "fid" / FidField
)

# size[4] Rclunk tag[2]
Rclunk = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rclunk.value, TypeField),
    "tag" / TagField
)

# size[4] Tremove tag[2] fid[4]
Tremove = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tremove.value, TypeField),
    "tag" / TagField,
    "fid" / FidField
)

# size[4] Rremove tag[2]
Rremove = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rremove.value, TypeField),
    "tag" / TagField
)

# size[4] Tstat tag[2] fid[4]
Tstat = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Tstat.value, TypeField),
    "tag" / TagField,
    "fid" / FidField
)

TimeField = construct.Int32ul

StatField = construct.Struct(
    "size" / construct.Int16ul,
    "type" / construct.Int16ul,
    "dev" / construct.Int32ul,
    "qid" / construct.Embedded(
        QidField
    ),
    "mode" / ModeField,
    "atime" / TimeField,
    "mtime" / TimeField,
    "length" / construct.Int64ul,
    "name" / StringField,
    "uid" / StringField,
    "gid" / StringField,
    "muid" / StringField
)

# size[4] Rstat tag[2] stat[n]
Rstat = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Rstat.value, TypeField),
    "tag" / TagField,
    "stat" / construct.Embedded(
        StatField
    )
)

# size[4] Twstat tag[2] fid[4] stat[n]
Twstat = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Twstat.value, TypeField),
    "tag" / TagField,
    "fid" / FidField,
    "stat" / construct.Embedded(
        StatField
    )
)

# size[4] Rwstat tag[2] 
Twstat = construct.Struct(
    "size" / SizeField,
    "type" / construct.Const(MessageType.Twstat.value, TypeField),
    "tag" / TagField
)
    
# class Message(typing.NamedTuple):
#     length: int
#     type: MessageType
#     tag: ...
    
