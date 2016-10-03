#!/usr/bin/env python
# -*- encoding: utf8 -*-
# -*- coding: utf8 -*-
# Functions used by with magic_database
import traceback

import regex
import struct


def _compact_whitespace(buff):
    """
    Returns a list only with the whitespaces in the string.
    The buff needs to have at least one blank space
    :param buff:
    :return:
    """
    rlist = ["", ]
    lastchar = None
    for char in buff:
        consecutives = ""
        if char == " ":
            rlist[-1]
        if char != " " and lastchar == " ":
            rlist.append("")
        lastchar = char
    return rlist


def _handle_flags(buff, item, flags):
    wflag = None
    if "t" in flags or "b" in flags:
        # Do nothing...
        pass
    if "W" in flags:
        if (not " " in buff) or (not " " in item):
            wflag = False
        buffl = _compact_whitespace(buff)
        iteml = _compact_whitespace(item)
        for i in buffl:
            if i in iteml:
                wflag = True
                break
            else:
                wflag = False
    if "w" in flags:
        buff = buff.replace(" ", "")
        item = item.replace(" ", "")
    if "c" in flags:
        # Do nothing, case sensitive matching is the default
        pass
    if "C" in flags:
        buff = buff.lower()
        item = buff.lower()
    if "T" in flags:
        buff = buff.strip()
    return buff, item, wflag


def _get_offset(fp, encoded_offset):
    """Handle hexadecimal indirect offsets"""
    encoded_offset = encoded_offset[1:-1]
    first = None
    second = None
    for char in "+-*/&|^":
        if char in encoded_offset:
            first, second = encoded_offset.split(char)
            break
    if not first:
        first = encoded_offset
    # by default kind is l (long)
    kind = "l"
    nsplit = first.split(".")
    first = nsplit[0]
    if len(nsplit) > 1:
        kind = nsplit[1]
    sizes = dict(b=1, i=4, s=2, l=4, B=1, I=4, S=2, L=4)
    kinds = dict(b="<b", i="<i", s="<h", l="<l", B=">B", I=">I", S=">H",
                 L=">L")
    fp.seek(int(first, 16))
    iof = fp.read(sizes[kind])
    indirect = struct.unpack(kinds[kind], iof)[0]
    if second:
        second = int(second)
        toeval = "%s %s %s" % (indirect, char, second)
        indirect_offset = eval(toeval)
    else:
        indirect_offset = indirect
    return indirect_offset


def get_buffer(fp, offset=0, chars=4096, flag=""):
    if isinstance(offset, basestring):
        try:
            offset = _get_offset(fp, offset)
        except ValueError:
            # FIXME: I don't know how to handle this
            offset = 0
    fp.seek(offset)
    if chars:
        str = fp.read(chars)
    else:
        str = fp.read()
    return str


def _handle_struct(buff, item, fmt):
    try:
        buff = struct.unpack(fmt, buff)
    except:
        return False
    try:
        item = struct.unpack(fmt, item[2:].decode("hex"))
    except Exception as e:
        return False
    return buff == item


def do_belong(fp, offset, item,):
    buff = get_buffer(fp, offset, chars=4)
    return _handle_struct(buff, item, ">L")


def do_lelong(fp, offset, item):
    buff = get_buffer(fp, offset, chars=4)
    return _handle_struct(buff, item, "<L")


def do_long(fp, offset, item):
    buff = get_buffer(fp, offset, chars=4)
    return _handle_struct(buff, item, "L")


def do_leshort(fp, offset, item):
    buff = get_buffer(fp, offset, chars=2)
    return _handle_struct(buff, item, "<h")


def do_beshort(fp, offset, item):
    buff = get_buffer(fp, offset, chars=2)
    return _handle_struct(buff, item, ">h")


def do_short(fp, offset, item):
    buff = get_buffer(fp, offset, chars=2)
    return _handle_struct(buff, item, "H")


def do_befloat(fp, offset, item):
    buff = get_buffer(fp, offset, chars=8)
    return _handle_struct(buff, item, ">f")


def do_bedouble(fp, offset, item):
    buff = get_buffer(fp, offset, chars=8)
    return _handle_struct(buff, item, ">d")


def do_lefloat(fp, offset, item):
    buff = get_buffer(fp, offset, chars=4)
    return _handle_struct(buff, item, "<f")


def do_ledouble(fp, offset, item):
    buff = get_buffer(fp, offset, chars=8)
    return _handle_struct(buff, item, "<d")


def do_regex(fp, offset, item, flags=""):
    buff = get_buffer(fp, offset)
    buff, item, wflag = _handle_flags(buff, item, flags)
    try:
        c = regex.compile(regex)
    except:
        return False
    result = c.search(buff, item)
    if wflag is not None:
        return result and wflag
    return result


def do_string(fp, offset, item, flags=""):
    chars = len(item)
    buff = get_buffer(fp, offset, chars=chars)
    buff, item, wflag = _handle_flags(buff, item, flags)
    result = buff == item
    if wflag is not None:
        return result and wflag
    return result


def do_search(fp, offset, item, srange="", flags=""):
    try:
        srange = int(srange)
    except ValueError:
        # Can't really compare if the rule is bad
        return False
    item = item.replace("\\", "")
    chars = len(item)
    buff = get_buffer(fp, offset, chars=chars)
    buff, item, wflag = _handle_flags(buff, item, flags)
    # Split in lines
    bufflist = buff.split("\n")
    # According to the documentation we need to check if item is in every
    # line until the 'srange' element.
    matchs = [k for k in bufflist[:srange] if item in k]
    if wflag is not None:
        return matchs and wflag
    return matchs


def do_byte(fp, offset, item):
    buff = get_buffer(fp, offset, chars=1)
    return item == buff
