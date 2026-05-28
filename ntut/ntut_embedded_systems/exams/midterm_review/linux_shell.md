> NTUT Embedded Systems <br> Midterm Review <br> Linux & Shell Scripting

**List of Linux commands**
|         |             |
|---------|-------------|
| `cd`    | Change current directory |
| `chmod` | Change file permissions |
| `chown` | Change owner |
| `chgrp` | Change group |
| `cp`    | Copy a file from one location to another |
| `ls`    | List contents of a directory |
| `mkdir` | Make a directory |
| `mv`    | Move or rename a file or directory |
| `find`  | Find files |
| `locate`| File locating program |
| `pwd`   | Print or list the present working dir with full path |
| `rm`    | Remove files |
| `rmdir` | Remove directory |
| `touch` | Change file timestamps to the current time |
| `whereis`| Locate the binary and man page files for a command |
| `which` | Show pull path of commands where given commands reside |

||File viewing and editing|
|---------|---------------|
| `emacs` | Full screen editor |
| `pico`  | Simple text editor |
| `vi`    | Editor with a command mode and text mode |
| `gedit` | GUI text editor |
| `tail`  | Look at the last  10 lines of a file |
| `head`  | Look at the first 10 lines of a file |

||File compression, backup, and restoring|
|--------------|-------------------------|
| `compress`   | Compress data |
| `uncompress` | Expand data |
| `cpio`       | Can store files on tapes |
| `gzip`       | Compress a file to a gz file |
| `gunzip`     | Uncompress a gz file |
| `tar`        | Archives files and directories and can store on tapes |
| `zip`        | Compress a file to a .zip file |
| `unzip`      | Uncompress a .zip file |
| `cat`        | View a file |
| `cmp`        | Compare two files |
| `cut`        | Remove sections from each line of files |
| `diff`       | Show the differences between files |
| `echo`       | Display a line of text |
| `grep`       | List all files with the specified expression |
| `sleep`      | Delay for a specified amount of time |
| `sort`       | Sort a file alphabetically |
| `uniq`       | Remove duplicate lines from a sorted file |
| `wc`         | Count lines, words, and characters in a file |
| `sed`        | Powerful stream editor |
| `awk`        | An extremely versatile programming language for working on files |

##
**1. What is Linux?**

> Linux is a Unix clone written from scratch by Linus Torvalds with assistance from a team of hackers across the Internet.

##
**2. What is Unix?**

> Unix is a multitasking, multi-user operating system developed in 1969 at Bell Labs.

##
**3. What is an "xterm" emulation software?**

> A software that emulates an "X" terminal and connects using the "SSH" Secure Shell Protocol.

##
**4. What is a shell?**

> A computer program that interprets the commands you type and sends them to the operating system. Secondly, it provides a programming environment consisting of different environment variables.

##
**5. What is the command to find out the shell your computer uses?**

```bash
echo $SHELL
```

##
**6. What does the pipe "|" symbol do?**

> It feels the OUTPUT of one command into the INPUT of another command.

##
**7. Why do we use shell scripting?**

> - Prepare input files, monitor jobs, process outputs
> - Useful to create own commands
> - Save time in file processing
> - Automate tasks such as system administration

##
**8. Write "Hello World!", the current date, and the current directory in the terminal using shell.**

```bash
echo Hello World!
echo The date today is `date`
echo The current directory is $directory
```

##
**9. What does "#!" mean at the top of a shell script?**

> Indicates the location of the shell that will be run to execute the script

##
**10. Explain the three different types of quote characters.**

> Double Quote (")
> - If a string is enclosed in "", the references to variables ($variable) are replaced by their values. Back-quote and escape (\) characters are treated specially.

> Single Quote (')
> - Everything inside is taken literally and nothing is treated as special.

> Back Quote (`)
> - Everything inside is treated as a command and the shell will attempt to execute it. If the execution is successful, the primary output from the command replaces the string.

##
**11. In the above example, if there are less than 3 items in the response, what will the trailing variables be set to?**

```bash
echo "Please enter three file names:"
read filea fileb filec
echo "These files are used: $filea $fileb $filec"
```

> blank ('')

##
**12. In a shell script, what type of variable will 'a' be?**

```bash
a=1234
```

> String

##
