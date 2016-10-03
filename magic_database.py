#!/usr/bin/env python
# -*- encoding: utf8 -*-
# -*- coding: utf8 -*-

#DATABASEFILE = "/opt/local/share/misc/magic"
#DATABASEFILE = "magic.db"
#DATABASEFILE = "magic_exe.db"

import magic_functions
import traceback


def is_line_allowed(line):
    """

    :param line:
    :return:
    """
    if not line:
        return False
    if line.startswith("#"):
        # Ignore comments
        return False
    if line.startswith("!:mime") or line.startswith("!:stregth") or \
            line.startswith("!:apple") or line.startswith("!:ext"):
        # Temporarily ignore this
        return False
    return True


class Rule:

    def __init__(self, offset, function, value, kind, counter):
        self.function = function
        self.value = value.replace("\\0", "\x00")
        self._kind = kind
        self.counter = counter
        self._matches = []
        self.child = []
        self._parent = None
        self.offset = self._clean_offset(offset)

    def __repr__(self):
        return "Rule %s with %d subrules" % (self._kind, len(self.child))

    def _clean_offset(self, offset):
        """The offset includes the ">" character that determines if this is
        a nested rule, removing them"""
        offset = offset.strip(">")
        # if offset.startswith("&"):
        #    offset = self.parent.offset
        if offset.isdigit():
            return int(offset)
        if offset.startswith("0x"):
            return int(offset, 16)
            # split = offset.split()
            # if len(split) == 1:
            #     return int(offset, 16)
            # else:
            # Malformed entry, uses space instead of tab between offset
            # and function
            #     offset, function = split
            # Fix the function, value and kind
            #     offset = self._clean_offset(offset)
            #     self._kind = self.value
            #     self.value = self.function
            #     self.function = function
            #     return offset
        return offset

    def add_rule(self, rule):
        if not isinstance(rule, Rule):
            return False
        self.child.append(rule)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def set_parent(self, parent):
        self._parent = parent

    def matches(self, fp):
        """Try to match the content of fp (file type object) with this rule,
        if matches then try to match the subrules."""
        fsplit = self.function.split("/")
        funcname = fsplit[0]
        args = []
        if len(fsplit) > 1:
            funcname = fsplit[0]
            args.extend(fsplit[1:])
        try:
            func = getattr(magic_functions, "do_%s" % funcname)
        except AttributeError:
            return False
        args.insert(0, self.offset)
        args.insert(1, self.value)
        resfunc = None
        try:
            resfunc = func(fp, *args)
        except Exception as e:
            pass
            # This is for debuggin purposes, should be removed or cached an
            # specific exception.
            # traceback.print_exc()
            # print fp, args
        if resfunc:
            self._matches.append(self._kind)
            for child in self.child:
                if child.matches(fp):
                    self._matches.append(child.kind)
            # print "Matches!", self, self.child, self.kind
            return self._matches

    @property
    def kind(self):
        return " ".join(self._matches)


def set_parent_rule(rule, parent_rule):
    # Get the counter of the "parent_rule"
    pcounter = parent_rule.counter
    parent = parent_rule.parent
    if rule.counter < pcounter:
        set_parent_rule(rule, parent)
    if rule.counter == pcounter:
        rule.parent = parent
        parent.add_rulep(rule)


def _get_meta(line):
    offset, function, value, kind = None, None, None, None
    try:
        offset, function, value, kind = [k.strip() for k in
                                         line.split(
                                             "\t") if k]
    except ValueError as e:
        # Probably there is no kind.
        try:
            offset, function, value = [k.strip() for k in
                                       line.split(
                                           "\t") if k]
            kind = ""
        except ValueError:
            pass
    return offset, function, value, kind


def parse_database_file():
    """Parse the database file and return rules to match and their result"""
    with open(DATABASEFILE, "r") as fp:
        allfile = fp.read()
        chunks = [k for k in allfile.split("\n\n") if k]
        rules = []
        parents = []
        lines = [k for k in allfile.split("\n") if k]
        last_counter = 0
        for line in lines:
            if not is_line_allowed(line):
                continue
            offset, function, value, kind = _get_meta(line)
            if offset == None:
                continue
            counter = offset.count(">")
            try:
                rule = Rule(offset, function, value, kind, counter)
            except ValueError:
                continue
            if counter == 0:
                parent = rule
                parents.append(rule)
                rules.append(rule)
                last_counter = 0
            if last_counter < counter:
                rule.parent = parent
                parent.add_rule(rule)
                last_parent = rule
            elif last_counter > counter:
                set_parent_rule(rule, last_parent)
            last_counter = counter

        return rules


if __name__ == "__main__":
    print parse_database_file()
