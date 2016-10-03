#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
# This module helps to determine the type of files using the libmagic rules


from __future__ import absolute_import

import os
import sqlite3

import sys

import magic_database
import magic_functions


def from_path(path, mode="rb"):
    """Returns the file type according to the magic type.

    * mode (string): determines the mode to open the file, default to "rb"
    """
    with open(path, "r") as fp:
        return path, from_file(fp)
    return


def from_file(fp):
    """Return the file type using a buffer."""
    rules = magic_database.parse_database_file()
    for rule in rules:
        if rule.matches(fp):
            if rule.kind:
                return rule.kind
    return ""


if __name__ == "__main__":
    for i in sys.argv[1:]:
        print ": ".join(from_path(i))
