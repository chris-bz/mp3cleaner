# MP3 Cleaner

MP3 Cleaner is a program that automates a boring task of editing mp3 tags in whatever way the user sees fit. It can save a lot of time both when used to "standardize" entire music collection, or when used daily on each freshly downloaded batch.

<br>
## How does it work?

1. The user sets all preferences in the settings.py file. It can take a while, but needs to be performed just once.
2. The program loads those settings on startup and starts scanning for loose tracks and album folders.
2. It extracts all tag data from mp3 files found, corrects them and saves this corrected tag information to a yaml file.
3. Images are renamed, converted and optimized, junk files are deleted, empty folders are removed, non-mp3 music files are moved to special directory.
4. When initial work is done, the file with tag data gets opened in a text editor of choice to enable final corrections.<sub>(this can be disabled in settings so entire work is done automatically)</sub>
5. The program reads saved yaml file clears tags in corresponding music files, writes corrected tag data, renames files based on tags, creates album directories for album files (again, according to the scheme specified in program options) and moves them there.
7. Finally, it performs few cleanup operations.

Altogether, it performs many small common operations that take an awful lot of time when performed by hand.

<br>
## What does it do?

Below is a list of (most of the) tasks the program performs. Many of those you can enable/disable or change in the settings.py file.

- automatically cleans tag data, leaving only most important tags
- can save to ID3v1.1 and/or one of the two: ID3v2.3, ID3v2.4
- capitalizes artist names, album names and track titles according to [Chicago Manual of Style](https://en.wikipedia.org/wiki/The_Chicago_Manual_of_Style)
- final corrections can (but don't have to) be made in a yaml file, automatically opened in an editor specified in settings.py
- moves albums and single files to custom directory
- creates album directories according to custom 'template'
- can set up own templates both for single and album mp3s
- checks if unwanted programs are running, does not start tagging until they are closed
- automatically removes 'feat.', 'featuring' etc. from artist and title tags
- converts smaller Roman numerals to Arabic numerals (useful when data is later scrobbled/parsed for statistics)
- moves guest artist names to artist tag where they belong, separated by comma
- deletes .nfo, .txt and other unwanted file types
- removes images below a specified size (usually no use for those 50px by 50px album covers)
- removes odd image types
- converts png to jpg files, compresses jpgs to 95% quality if initial is higher
- tries to guess image content (front cover, back cover...) and renames files accordingly
- checks album length and if it's shorter than 30 minutes, adds 'EP' to title
- converts various 'soundtrack' title additions to OST (or any other text)
- removes redundant junk like '(Original Mix)' from track titles
- removes 'produced by' title endings information (it's not part of title and every track is produced by someone, so leaving those makes titles inconsistent)
- removes 'bonus track' title endings
- track titles with 'instrumental' annotation always get '(instrumental)' at the end (and not '(instr.)' or '[ Instrumental )')
- preserves '/' in album titles, but in folder names substitutes it with '#' (former can't be used in directory names)
- lowercases 'cover', 'edit', 'live', puts them in round brackets
- moves non-mp3 music files to special directory, as this program is only equipped to deal with mp3 files (it has too many dependencies as it is)

<br>
## Requirements

1. **Linux**
MP3 Cleaner was not tested on Windows. All file and directory operations are done through Python tools, and not Linux commands. Therefore, it is possible that the cleaner will run bug-free on Windows with just minimum dependencies installed. But then you won't have proper capitalization, file repairing and image handling.
2. [Python](https://www.python.org/downloads/)
MP3 Cleaner is a Python file. It requires version 3.6 or higher. You can check which version you have installed (and if it's installed at all) by writing 'python' in command line and pressing Enter.
3. [Pip](https://pypi.org/project/pip/)
Python package manager. It will automatically install remaining dependencies with simple command. If you've installed Python from official website, pip got installed as well.

You can check if it's installed by writing 'pip' in command line and pressing Enter. See if it says that such program doesn't exist on your system. If that is the case, follow installation instructions on package manager's official website linked above.
4. [eyed3](https://eyed3.readthedocs.io/en/latest/)
A wonderful tag editor written in Python, conveniently available both as command line tool and importable Python library. The program uses the latter for all tag-related tasks. It can be installed by executing this command in your terminal emulator: 'pip install eyed3'.

<br>
### Optional

The tools listed below are optional, but recommended.

1. [mp3val](http://mp3val.sourceforge.net/)
A very handy mp3 repairing tool written in C. If installed and enabled, one of the first things MP3 Cleaner does is running mp3val on all mp3 files found, checking them for errors and sorting them out. It makes MP3 Cleaner's total execution time slower by many dozen times, but it's still many dozen times faster than re-downloading all damaged files ;) It also protects against potential bugs resulting from faulty tag readings.
2. [spacy](https://spacy.io/)
One of many natural language processing tools. It is necessary for proper word capitalization. Install with 'pip install spacy' command.
3. [jpegoptim](https://www.mankier.com/1/jpegoptim)
A very good tool for optimizing jpg images. It can significantly reduce image file size while retaining high quality. Useful for image cleanup purposes, especially if we often find uncompressed full booklet scans in album folders. 
4. [Image Magick](https://imagemagick.org/index.php)
A classic command-line image editor. Needed for png to jpg conversion. On some Linux distributions it comes pre-installed. Run '*mogrify*' in command line and see if you get an error, in which case it's not installed. 
On Ubuntu/Mint/Debian etc. you can install both IM and jpegoptim with one command: 'sudo apt-get install imagemagick jpegoptim'. If your OS has different package manager, use its own commands to check if they are present in official repositories. If they're missing, consult official website for instructions on manual installation.

<br>
### No need for...

1. YAML

MP3 Cleaner uses a YAML file as intermediary. All tags are read, pre-corrected and saved to it, and after user corrections (or automatically, if user corrections are disabled), its being read to save its content to mp3 tags.

The format is very readable (which is important when many tags are manually corrected), but that's probably the only good thing that can be said about YAML. To avoid million bugs that it brings to the table, the program parses it as a standard string.

The happy side effect of it is one less dependency to worry about, as otherwise program user would have to install its Python parser through pip.

The tag changes file is still valid YAML, in case you would want to parse and process that data on his own. Just be aware that working with parsed YAML is almost always more trouble than it's worth.

<br>
## Additional notes
MP3 Cleaner uses Stephen Jung's NLP Chicago Manual of Style instructions for word capitalization. His solution has been imported, trimmed and converted to a function. [Here](https://github.com/tummychow/titlechaser) is its Github page.

<br>
## How to use it?

1. download both python files (or git clone entire repository), put them both in one directory
2. open the file in any text/code editor and **edit all the program settings**. you need to tell the program:
- where it's supposed to look for mp3 files
- where to send them when tag editing is done
- what text editor you have installed and want to use to correct tag data

...and few other things. The program is pretty flexible for its size, much of its behavior can be tuned as everyone has different needs ;)
3. after the program is configured, just double-click on it from your file manager, or run it from command line with *./path/to/mp3cleaner.py*
