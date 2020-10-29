# MP3 Cleaner

MP3 Cleaner is a program that automates the boring task of editing mp3 tags in whatever way the user sees fit. It can save a lot of time both when used to "standardize" entire music collection, or when used daily on each freshly downloaded batch.

## How does it work?
1. The user sets all the preferences in settings.py file. It can take a while, but needs to be performed once.
2. The script loads that file, checks a specified folder for loose tracks and album folders.
2. It extracts all tag data from mp3 files found, corrects them and saves this corrected tag information to a yaml file.
3. Images are renamed, converted and optimized, junk files are deleted, empty folders are removed, non-mp3 music files are moved to special directory.
4. When the initial work is done, the file with tag data gets opened in a text editor of choice to check if all tags are done well. Inside that file, the user can make whatever corrections needed.
5. Program waits until the user finishes making changes, comes back to console and presses Enter.
6. The program then takes each mp3 file, clears tags, writes tag data specified in a file, renames files based on tag data, creates album directories for album files (again, according to the scheme specified in program options) and moves them there.
7. Finally, it performs few cleanup operations.

Altogether, many small repeated operations that take an awful lot of time when performed by hand.

## What does it do?

Below is a list of (most of the) tasks the program performs. Many of those you can enable/disable or change in the settings.py file.

- automatically cleans tag data, leaving only most important tags
- can save to ID3v1.1 and/or one of the two: ID3v2.3, ID3v2.4
- capitalizes artist names, album names and track titles according to the [Chicago Manual of Style](https://en.wikipedia.org/wiki/The_Chicago_Manual_of_Style)
- final corrections can (but don't have to) be made in a yaml file, automatically opened in an editor specified in settings.py
- moves albums and single files to custom directory
- creates album directories according to custom 'template'
- can set up own templates both for single and album mp3s
- checks if unwanted programs are running, does not start tagging until they are closed
- automatically removes 'feat.', 'featuring' etc. from artist and title tags
- converts smaller Roman numerals to Arabic numerals (useful when the data is later scrobbled/parsed for statistics)
- moves guest artist names to artist tag where they belong, separated by comma
- deletes .nfo, .txt and other unwanted file types
- removes odd image types
- converts png to jpg files, compresses jpgs to 95% quality if initial is higher
- optimizes images to save space
- tries to guess image content (front cover, back cover...) and renames files accordingly
- checks album length and if it's shorter than 30 minutes, adds 'EP' to title
- converts various 'soundtrack' title additions to OST (or any other text)
- removes redundant junk like '(Original Mix)'
- removes title endings 'produced by' information - it's not part of title and every track is produced by someone, so leaving those makes titles inconsistent
- removes title endings 'bonus track'
- track titles with 'instrumental' annotation always get '(instrumental)' at the end (and not '(instr.)' or '[ Instrumental )')
- preserves '/' in album titles, but in folder names substitutes it with '#' (former can't be used in directory names)
- lowercases 'cover', 'edit', 'live', puts them in round brackets
- removes images below a specified size (usually no use for those 50px by 50px album covers)
- moves flac and few other music formats to special directory, as this program is only equipped to deal with mp3 files (it has too many dependencies as it is)

## Requirements
1. **Linux**
The program uses Linux applications. Therefore, it can only run on Linux as of today.
2. [Python](https://www.python.org/downloads/)
MP3 Cleaner is a Python file. It requires version 3.6 or higher. You can check which version you have installed (and if it's installed at all) by writing 'python' in command line and pressing Enter.
3. [Pip](https://pypi.org/project/pip/)
Python package manager. It will automatically install our remaining dependencies with simple command. If you've installed Python from official website, pip got installed as well.
You can check if it's installed by writing 'pip' in command line, pressing enter and checking if it says that such program doesn't exist on your system. If that is the case, install pip from instructions on the package manager's official website linked above.
4. [eyed3](https://eyed3.readthedocs.io/en/latest/)
A wonderful tag editor written in Python, conveniently available both as a command line tool and an importable Python library. The program uses the latter for all tag-related tasks.

### Optional

The tools listed below are optional, but recommended.

1. [spacy](https://spacy.io/)
One of many natural language processing tools. It is necessary for proper word capitalization.
Both will be installed when executing this command in your terminal emulator:
> pip install eyed3 spacy
2. [jpegoptim](https://www.mankier.com/1/jpegoptim)
A very good tool for optimizing jpg images. It can significantly reduce image file size while retaining high quality. Useful for image cleanup purposes, especially if we often find uncompressed full booklet scans in album folders. 
3. [Image Magick](https://imagemagick.org/index.php)
A cult command-line image editor. Needed for png to jpg conversion. On some Linux distributions it comes pre-installed. Run '*mogrify*' in command line and see if you get an error, in which case it's not installed. 
On Ubuntu/Mint/Debian etc. you can install both IM and jpegoptim with one command:
> sudo apt-get install imagemagick jpegoptim
If your OS has different package manager, use its own commands to check if they are present in official repositories. If they're missing, consult official website for instructions on manual installation.
8. [mp3val](http://mp3val.sourceforge.net/)
A very handy mp3 repairing tool written in C. If installed and enabled, at the start of mp3 cleaner, mp3val is run on all mp3 files found, checks them for errors and sorts them out. It makes mp3 cleaner's total execution time slower by many dozen times, but it's still many dozen times faster than re-downloading all damaged files ;)

### No need for...
1. YAML 
MP3 Cleaner uses a YAML file as intermediary. All tags are read, pre-corrected and saved to it, and after user corrections (or automatically, if user corrections are disabled), its being read to save its content to mp3 tags.

The format is very readable (which is important when many tags are read), but overall it is a horrible mess in my opinion. To avoid million bugs that it brings to the table, the program parses it as a standard string.

The happy side effect of it is one less dependency to worry about, as otherwise the user would have to install its Python parser through pip.

The tag changes file is still valid YAML, in case the user would want to parse and process that data on his own.

## Additional notes
MP3 Cleaner uses Stephen Jung's NLP Chicago Manual of Style instructions for word capitalization. His solution has been imported, trimmed and converted into a function. [Here](https://github.com/tummychow/titlechaser) is its Github page.

## How to use it?
1. download both python files (or git clone entire repository), put them both in one directory
2. open the file in any text/code editor and **edit all the program settings**. you need to tell the program:
- where it's supposed to look for mp3 files
- where to send them when tag editing is done
- what text editor you have installed and want to use to correct tag data
...and few other things. The program is pretty flexible for its size, much of its behavior can be tuned as everyone has different needs ;)
3. after the program is configured, just double-click on it from your file manager, or run it from command line with *./path/to/mp3-cleaner.py*
