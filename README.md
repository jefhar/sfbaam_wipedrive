# SFBAAM Wipedrive

Using Wipedrive to wipe drives creates an XML file named by server serial number.

The boss wants the files organized by drive size. This moves the files into buckets
labelled by drive size. Before the files get here, they are all dumped into a common
directory, where file name collisions are already resolved.

This relies upon the fact that Wipedrive XML files have a consistent schema.

Create the dockerfile:
```
docker build -t wipedrive .
```

Run the image:
```
docker run -it --rm -v"($ROOT_DIRECTORY_OF_ALL_XML_FILES):/app" wipedrive
flattendirs /app
move_wipedrive --help
```

## Usage
### flattendirs
`flattendirs` takes a single argument, the name of your root directory. In the example listed above, that would be
`/app` directory. This short script removes spaces from directories and files, then moves the resulting files to the
root directory. A file originally named `/app/foo/New Folder/12345.txt` would be renamed
`/app/foo_New_Folder_12345.txt`. This allows `/app/A1/Q345.xml` and `/app/A2/Q345.xml` to both be nestled in the root
directory so `move_wipedrive` can reorganize the files.


### move_wipedrive
`usage: move_wipedrive_xml -s <sourcePath> -o <outputPath> -p <partitions> [-f]`

`sourcePath` in the above docker command would be `/app`. This is where the files have been flattened. If your
`outputPath` is not inside the `sourcePath`, make sure you attach it as a volume to your docker container, otherwise you
may not be able to retrieve your files.

The `-p` parameter defines a positive integer of partitions to organize the resulting files. A partition level of 3 will
move `Q345678.pdf` to `Q/3/4/Q345678.pdf`. Beneficial if you have large numbers of servers with similar serial numbers
performing the drive wipes. Given `-p0`, `move_wipedrive` will move the file to `/Q345678.pdf`.

The `-f` parameter will force an output file to be re-written.

#### Why
In our environment, a drive is wiped, and the resulting XML log and PDF file are named `log.xml` and `log.pdf`. The
technician then renames the xml and PDF so they aren't overwritten by the next wipe. After a few captures, the files are
dumped to a network file storage.

Since we usually wipe drives of the same size at the same time, the files usually contain information about the same
sized hard drives. `move_wipedrive` solves the issue of uniquely renaming the XML and matching PDF files, organizing
them into a hierarchal directory structure, first by drive size, then wiping server's serial number.

\#python
