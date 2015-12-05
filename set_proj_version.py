#!/usr/bin/python
"""
Sets the version number for one or more Delphi or C++Builder project files.
Tested on Windows and Linux.

Includes the ability to automatically process all member projects if given a
project group file.

Also updates the copyright year (if a copyright year is present).

The current version has a couple of limitations: it always treats file version
and product version as the same, and it always sets the build number to 0.

For simplicity, and to avoid munging RAD Studio project files more than we
have to, we process project files as text, not XML.
"""

from __future__ import print_function

from datetime import datetime
import os
from os.path import dirname, join, normpath
import re
import sys

if len(sys.argv) < 3:
    print("Usage: %s version dproj [ cbproj ... ]" % sys.argv[0], file=sys.stderr)
    print("You can also provide a groupproj to process all of its included dproj/cbproj.", file=sys.stderr)
    sys.exit(2)

now = datetime.now()

# Get and process the version number
version = sys.argv[1]
if not re.match('\d+\.\d+\.\d+$', version):
    print("Bad version number %s" % version, file=sys.stderr)
    print("Only major.minor.release format is currently supported." % version, file=sys.stderr)
    sys.exit(2)
parts = dict(zip(['MajorVer', 'MinorVer', 'Release'], [int(n) for n in version.split('.')]))
parts['Build'] = 0
version = version + '.' + str(parts['Build'])


def process_proj(filename):
    print("Updating %s..." % filename)
    tmp_filename = filename + '.tmp'
    with open(filename, 'rb') as file_in:
        with open(tmp_filename, 'wb') as file_out:
            for line in file_in:

                # Check for projects included within a groupproj.
                m = re.search(r'<Projects Include="(.*)"', line)
                if m:
                    subproj_filename = m.group(1)

                    # Use Unix-compatible path separators, in case we're
                    # running on Linux or OS X.
                    subproj_filename = subproj_filename.replace('\\', '/')

                    subproj_filename = normpath(join(dirname(filename), subproj_filename))
                    process_proj(subproj_filename)

                # XE-style version number parts don't appear in every
                # PropertyGroup and are omitted if 0.  To handle this, track
                # which parts we've seen and insert missing parts if needed.
                if re.search('<PropertyGroup', line):
                    seen = set()
                m = re.search(r'(\s*)</PropertyGroup>', line)
                if m and seen:
                    for key, value in parts.items():
                        if (key not in seen) and value != 0:
                            file_out.write('%s\t<VerInfo_%s>%s</VerInfo_%s>\r\n' % (m.group(1), key, value, key))

                # Update references to the version number.
                for key in ['FileVersion', 'ProductVersion']:
                    # RAD Studio 2010
                    line = re.sub(
                        r'<VersionInfoKeys Name="%s">[0-9.]+</VersionInfoKeys>' % key,
                        r'<VersionInfoKeys Name="%s">%s</VersionInfoKeys>' % (key, version),
                        line)

                    # RAD Studio XE2
                    line = re.sub(
                        r'%s=[0-9.]+' % key,
                        r'%s=%s' % (key, version),
                        line)

                # Update references to any parts of the version number.
                for key, value in parts.items():
                    if re.search(r'<VerInfo_%s>' % key, line):
                        seen.add(key)

                    # RAD Studio 2010
                    line = re.sub(
                        r'<VersionInfo Name="%s">\d+</VersionInfo>' % key,
                        r'<VersionInfo Name="%s">%s</VersionInfo>' % (key, value),
                        line)

                    # RAD Studio XE2
                    line = re.sub(
                        r'<VerInfo_%s>\d+</VerInfo_%s>' % (key, key),
                        r'<VerInfo_%s>%s</VerInfo_%s>' % (key, value, key),
                        line)

                # Update copyright year.
                for pre, post in [
                        ('<VersionInfoKeys Name="LegalCopyright">', '</VersionInfoKeys>'),
                        ('LegalCopyright=', ';')
                        ]:
                    line = re.sub(
                        r'%s(.* \d{4}-)\d+%s' % (pre, post),
                        r'%s\g<1>%s%s' % (pre, now.year, post),
                        line)
                    line = re.sub(
                        r'%s(.* \d+)%s' % (pre, post),
                        r'%s\g<1>-%s%s' % (pre, now.year, post),
                        line)

                file_out.write(line)
    os.remove(filename)
    os.rename(tmp_filename, filename)


for proj_file in sys.argv[2:]:
    process_proj(proj_file)
