#!/usr/bin/env python3

# This is a configuration file for mp3 cleaner. Here, you can customize
# how the program will operate. It is a Python file, so if you don't
# know the language, be sure to follow the rules below:
# * for fields that have single quotes, those quotes have to be filled
# * for fields which enable/disable some functionality, enable
#   with True, disable with False, with no quotes around
# * for fields with numbers, also do not use quotes



# FILE SETTINGS:
# All fields in this section except 'text_editor' need to be filled.
# Setting  up base_dir to be on the same partition as dest_dir will
# speed things up considerably.

# Folder with mp3s to clean
base_dir         = '/mnt/files/download/music'

# Folder where cleaned files will be moved. Albums will be put in
# subdirectories.
dest_dir         = '/mnt/files/music'

# Path to file which will store last batch of tag changes. If missing,
# the program will create one.
tag_changes_file = '/mnt/files-ssd/doc/scripts/logs/tag-changes.yaml'

# Name for directory where broken files will be moved. Subdirectory
# of base_dir.
broken_dir       = '.broken'

# Console command to start your text editor of choice. If left empty,
# all corrections will be done automatically.
text_editor      = 'subl'



# DEPENDENCIES (install first before enabling)

# On startup, scan all files for errors and repair them with mp3val.
# * mp3val can be easily installed on some Linux distros. for example,
#   it is present in Ubuntu's official repository, so this command will
#   install it: 'sudo apt-get install mp3val'
# * if it's not in your distro's official repo, get it from its official
#   website: http://mp3val.sourceforge.net/
enable_mp3val    = True

# Use Chicago Manual of Style capitalization instructions in Spacy.
# * Spacy needs to be installed for this to work, which can be done
#   with this command: 'pip install spacy'
# * if you don't have pip installed (and therefore can't install Spacy),
#   download Python from its official website, as new Python version
#   install files come with Pip included:
#   https://www.python.org/downloads/
# * if you disable it with False, first letter of every word will be
#   capitalized before final case optimizations, which will lowercase
#   some words
enable_nlp       = True



# EXTRA FUNCTIONALITY:

# The program will check every application from this list and if any is
# running, the program won't run. Useful not to start cleaning tags
# while something like Soulseek or torrent client is in the middle of
# downloading an album into base_dir directory. Write is like this:
#                  ['name1', 'name2', 'name3']
app_blacklist    = ['soulseek']

# Enable/disable adding ' EP' to album names for albums that are less
# than x seconds long.
ep_eval          = True

# Above the number of seconds specified below, release is considered
# an album and therefore won't add ' EP' to album name if ep_eval is set
# to True. If ep_eval is set to False, this setting does nothing.
ep_max_length    = 1800

# Try to convert Roman numerals to Arabic numerals. Useful for
# statistics, but alters original titles, which not everyone likes.
roman_to_arabic  = True

# The program will delete all images below specified size (in bytes),
# assuming they are too small, or badly compressed. If you want to keep
# all images, just set it to 0.
img_min_size     = 15360

# Convert png images to jpg, compress any jpg image whose compression
# level is 100 (meaning it is not compressed).
# * 95 gives great quality and mediocre file sizes
# * 90 gives very good quality with more space saved
# * 80 gives ok-ish image quality and saves plenty of space
# * better not to go below 80
img_conv_compr   = True
jpg_compr_lvl    = 95



# TEXT REMOVALS
# * set to True to delete items described in corresponding comments
# * set to False to leave them unchanged

# Delete variants of 'bonus track', like in 'Track Name (bonus track)'
# or in 'Track Name [ bonus track ]'.
del_bonus_track  = True

# Delete variants of 'explicit' (often added in hip-hop music
# to indicate that the track contains un-beeped cursing).
del_explicit     = True

# Delete variants of the word 'LP'. It indicates full-length release,
# but adding EP to all shorter length materials is indicating enough;
# if the album title doesn't have EP, it's a long-play, and so putting
# 'LP' is overkill.
del_lp           = True

# Delete variants of 'original mix' - most redundant information that's
# regularly used in mp3 tags, particularly in electronic music.
del_orig_mix     = True

# Delete variants of 'produced by', often present in title tag, which is
# probably not the place for it.
del_produced     = True


# TEXT REPLACEMENTS
# Specify replacement text for patterns described in each variable's
# corresponding comment...
# * to make no replacement, just leave empty quotes like so:
#   chn_something  = ''
# * replacements take care of capitalization, braces, brackets
#   and spaces around, ensuring that they are (almost) always
#   formatted the way we want

# Replace variants of '(edit)' with...
# Remember to start with space if default replacement string starts
# with it, otherwise you will end up with 'Track Name(edit)'.
chn_edit         = ' (edit)'

# Replace variants of '(extended)'
chn_extended     = ' (extended)'

# Replace variants of '(extended mix)'
chn_extended_mix = ' (extended mix)'

# Replace variants of '(instrumental)'
chn_instrumental = ' (instrumental)'

# Replace variants of '(live)'
chn_live         = ' (live)'

# Replace variants of 'ost', a short version of 'original soundtrack'
chn_ost          = ' OST'

# Replace variants of original|motion|picture|soundtrack|album.
# * looks for words 'original' and 'soundtrack', catches few other
#   common words around them
# * having one common identifier for soundtracks is especially useful
#   when listening history is processed, as it enables easy
#   identification without needing ID3v2 tag with genre properly set,
#   especially that scrobbling rarely includes genre information
chn_orig_sdtrack = ' OST'

# Replace variants of '(cover)'
chn_cover        = '(\1 cover)'

# Replace variants of '(some mix)', where 'some' can by any single
# or multiple words preceding the word 'mix'.
# * does not alter these preceding words
# * '\1' is a regex capturing group, best to leave untouched if you
#   don't know what those are
# * change the way the word 'mix' is capitalized
# * you can safely replace parentheses too with whichever symbols
#   you want
# * keep in mind that if you set chn_extended_mix ending as 'Mix'
#   or 'mix', this change will replace it with whatever you set here
chn_mix          = r' (\1 mix)'

# Replace general instances of words: 'Remix' and 'remix'.
# * leaving the field blank will usually result in an uppercase word
chn_remix        = 'remix'

# Replace variants of the word 'remix' inside brackets, braces
# and parentheses
chn_remix2       = ' (remix)'

# Same as chn_mix
# * if you spell the word 'remix' differently than in chn_remix, this
#   version will overwrite the spelling of the word for instances
#   which have preceding words and come surrounded with brackets,
#   braces and parentheses
chn_remix3       = r' (\1 remix)'

# Replace all instances of 'Reprise' and 'reprise' found
chn_reprise      = 'reprise'

# Same as chn_mix, but with 'version' ending
chn_version      = r' (\1 version)'


# OTHER

# Regex pattern to search for extra artists in artist and title tags.
# Best to leave unchanged.
feat_rgx         = ' ?[\[\( ]f(ea|)t[^ ]*\.? '
