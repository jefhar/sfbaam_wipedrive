# SFBAAM Wipedrive

Using Wipedrive to wipe drives creates an XML file named by server serial number.

The boss wants the files organized by drive size. This moves the files into buckets
labelled by drive size. Before the files get here, they are all dumped into a common
directory, where file name collisions are already resolved.

This relies upon the fact that Wipedrive XML files have a consistent schema.

This requires the following modules:
```
getopt
os
sys
xml.etree.ElementTree as ET
sty
```
\#python
