#!/usr/bin/python
"""
Tidies a Delphi or C++Builder project file, making it easier to track in
version control or compare in a diff tool like Beyond Compare.
"""

from __future__ import print_function

from xml.dom.minidom import parse, Text
import sys
import operator


def sort_child_nodes(xml_document, tag, sort_params):
    for parent in xml_document.getElementsByTagName(tag):
        children = []
        indenter = None
        last_indenter = None
        for child in parent.childNodes:
            if child.nodeType == child.TEXT_NODE:
                indenter = indenter or child
                last_indenter = child
            children.append(child)
        for child in children:
            parent.removeChild(child)
        children = filter(lambda node: node.nodeType != node.TEXT_NODE, children)
        for child in sorted(children, **sort_params):
            parent.appendChild(indenter.cloneNode(True))
            parent.appendChild(child)
        if last_indenter:
            parent.appendChild(last_indenter.cloneNode(True))


def create_ordering_dict(iterable):
    """Example: converts ['None', 'ResFiles'] to {'None': 0, 'ResFiles': 1}"""
    return dict([(a, b) for (b, a) in dict(enumerate(iterable)).iteritems()])


item_order = create_ordering_dict([
    'None', 'ResFiles', 'LibFiles', 'CppCompile', 'DelphiCompile',
    'ResourceCompile', 'FormResources', 'BuildConfiguration'])


def cmp_proj_item(a, b):
    if a.tagName not in item_order:
        return 1
    if b.tagName not in item_order:
        return -1
    return (
        cmp(item_order[a.tagName], item_order[b.tagName]) or
        cmp(a.getAttribute('Include').lower(), b.getAttribute('Include').lower()))


def sort_project(proj):
    sort_child_nodes(proj, "PropertyGroup", {'key': operator.attrgetter('tagName')})
    sort_child_nodes(proj, "ItemGroup", {'cmp': cmp_proj_item})

    # The Deployment node in newer versions of RAD Studio may have several
    # types of children. For example:
    #  - <ProjectRoot Name="$(PROJECTNAME)" Platform="Win32"/>
    #  - <DeployFile Class="ProjectFile" Configuration="Debug" LocalName="Project1.res">
    #  - <DeployClass Name="ProjectOutput" Required="true">
    # To accommodate, we consider the tag name and several attributes.
    sort_child_nodes(
        proj, "Deployment",
        {'key': lambda v: (v.tagName, v.getAttribute('Name'), v.getAttribute('Class'), v.getAttribute('LocalName'))})

    # Workaround for minidom bug; some attributes may be set to None instead
    # of the empty string, so writing them will fail.  May no longer apply
    # for current releases; untested.
    for element in proj.getElementsByTagName("BorlandProject"):
        if element.getAttribute("xmlns") is None:
            element.setAttribute("xmlns", '')


def add_build_orders(proj):
    """Adds comments to numeric build orders indicating what goes before what.
    For example, inserting a file at the beginning of the build order will
    cause a cascade of changes to numeric BuildOrders after it, but the
    comments indicating the relative order will remain unchanged."""
    def build_order_int(node):
        """Gets the numeric build order from a BuildOrder node."""
        return int(node.childNodes[0].wholeText)

    def sanitize_filename(f):
        return f.replace('--', '__')

    def build_order_before(build_order, current_build_order):
        while current_build_order > 0:
            if (current_build_order - 1) in build_order:
                return sanitize_filename(build_order[current_build_order - 1])
            current_build_order -= 1
        return None

    build_order = {}
    for node in proj.getElementsByTagName('BuildOrder'):
        build_order[build_order_int(node)] = node.parentNode.getAttribute('Include')
    for node in proj.getElementsByTagName('BuildOrder'):
        current_build_order = build_order_int(node)
        if build_order_before(build_order, current_build_order):
            indentation = node.previousSibling

            node.parentNode.insertBefore(
                proj.createComment("after " + build_order_before(build_order, current_build_order)),
                node.nextSibling)

            # Try to preserve indentation by copying existing indentation node.
            if isinstance(indentation, Text):
                node.parentNode.insertBefore(indentation.cloneNode(True), node.nextSibling)


if __name__ == '__main__':
    if not (2 <= len(sys.argv) <= 3):
        print("Usage: %s proj [output-file]" % sys.argv[0], file=sys.stderr)
        sys.exit(2)

    if len(sys.argv) > 2:
        sys.stdout = open(sys.argv[2], 'w')

    proj = parse(sys.argv[1])

    sort_project(proj)
    add_build_orders(proj)

    print(proj.toxml())

# vim: set ts=4 sw=4 et ai
