# Marco's project: Abracadabra

Abracadabra is not magic, but works with it!.

Abracadabra is a 100% python implementation of the UNIX command `file` (althought still incomplete). What Abracadabra do is parse libmagic "magic" file and then iterate over the rules described there trying to match the file type. If found it returns the file type.

    ➜  Marco git:(master) ✗ ./abracadabra.py common.pyc
    common.pyc: python 2.7 byte-compiled
    ➜  Marco git:(master) ✗ ./abracadabra.py abracadabra.py
    abracadabra.py: Python script text executable

## Missing stuff:
 * Return mime type

## Known issues:
 * Indirect offsets are not working correctly (althought I've followed the documentation) affecting binary detection

## Notes
 * libmagic database configuration is hardcoded in `magic_database.py`
