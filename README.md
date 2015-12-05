# RAD CLI

A collection of command-line tools and utilities for Embarcadero
[RAD Studio](http://www.embarcadero.com/products/rad-studio)
(Delphi and C++Builder).

All scripts require [Python 2.7](https://www.python.org/download/releases/2.7/)
to run.

## `tidy_proj.py`

Tidies up a `.dproj`, `.cbproj`, or `.groupproj` file, organizing the various
keys and attributes and file listings, to make it easier to track in version
control or compare in a diff tool like Beyond Compare.  (See
[RSP-11308](https://quality.embarcadero.com/browse/RSP-11308)
for more details on why this is important.)

`tidy_cbproj.py` also adds comments explaining files' build orders, to make
changes to build orders easier to understand when viewing diffs of project
files.

### Sample usage: Beyond Compare integration

To configure [Beyond Compare](http://www.scootersoftware.com/) to automatically
tidy project files when comparing them:

1. In Beyond Compare, go under Tools, under File Formats.
2. Click "New..."
3. Choose "Text Format" and click OK.
4. Enter a name of "Embarcadero Project File."
5. For "Mask", use the following:

    ```
    *.cbproj;*.cbproj.local;*.groupproj;*.groupproj.local;*.dproj;*.dproj.local
    ```
6. Under the Conversion tab, set Conversion to "External program (Unicode filenames).
7. For "Loading:", enter the following:
    ```
    c:\Python27\python.exe path\to\RadCli\tidy_proj.py %s %t
    ```

## `set_proj_version.py`

Sets the version number for one or more Delphi or C++Builder project files.

There are a couple of good options for setting a project's version number(s):
[DDevExtensions](http://andy.jgknet.de/blog/ide-tools/ddevextensions/) offers
a nice GUI (along with many, many other useful features), while
[this Embarcadero Community post](https://community.embarcadero.com/blogs/entry/change-dproj-file-and-product-version) provides a simple Delphi console app for
command-line use.  Compared to that, `set_proj_version.py` has a couple of
unique features:

* It can update several files at once.  If passed a `.groupproj`, it updates
  every member of the `.groupproj`.
* It can automatically update the copyright year (if present) as well as
  version numbers.
* It's cross-platform, in case you want to manage your releases from a
  non-Windows machine.
* It probably supports more versions of RAD Studio, although I haven't
  extensively tested this.

### Sample usage:

```
c:\Python27\python.exe path\to\RadCli\set_proj_version.py 1.2.3 MyProject1.dproj MyProject2.cbproj MyLibraries.groupproj
```

