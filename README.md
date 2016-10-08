# Abracadabra

Abracadabra is not magic, but works with it!

Abracadabra is a pure-Python implementation of the UNIX command `file` (although still incomplete). What Abracadabra does is parse libmagic's "magic" file and then iterates over the rules described there trying to match the file type. If found it returns the file type.

    ➜  Marco git:(master) ✗ ./abracadabra.py common.pyc
    common.pyc: python 2.7 byte-compiled
    ➜  Marco git:(master) ✗ ./abracadabra.py abracadabra.py
    abracadabra.py: Python script text executable

## Missing stuff:
 * Return mime type

## Known issues:
 * Indirect offsets are not working correctly (although I've followed the documentation) affecting binary detection

## Notes
 * libmagic database configuration is hardcoded in `magic_database.py`
