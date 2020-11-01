#!/usr/bin/env python3

# MP3 Cleaner - automatic tag cleaning, file validating, proper title
# capitalizing, junk fields removal, album art processing.
# Copyright (C) 2020 Christopher Blachewicz (call911@pm.me)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import re
import sys
from glob       import glob
from os         import (devnull, listdir, makedirs, path, popen, remove,
                        renames, rmdir, walk)
from subprocess import DEVNULL, PIPE, run

import eyed3

import settings as s
if s.enable_nlp:
    import spacy



class NoStdErr:
    '''Dumps all errors during code execution to /dev/null.'''
    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr            = open(devnull, 'w')
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._original_stderr


def report_current(filename):
    '''Prints which file is being worked and total queue size.'''
    global curr_file

    curr_file             += 1
    len_of_total_files_str = len(str(total_n_of_files))
    format_pre_str         = '{:' + str(len_of_total_files_str) + '}'
    curr_file_formatted    = format_pre_str.format(curr_file)

    print(f' [{curr_file_formatted}/{total_n_of_files}]  {filename}')


def eval_total_files():
    '''Counts all files to be edited in the base_dir directory'''
    n = 0

    for (root, dirs, files) in walk(s.base_dir):
        if not s.broken_dir in root and not s.notmp3_dir in root:
            n += len(files)

    if not n:
        raise ValueError(
          f'No mp3 files found in {s.base_dir}. Add something '
          ' (or change the path in program settings) and then start '
          'the program. Exiting...')
    return n


def tag_to_file(filepath, category='single', **kwargs):
    '''
    Reads tag information and saves it to a file. 

    Extracts file information from an mp3 file, does minor corrections
    and appends extracted yaml stripe to tag_changes_file. The 'category'
    argument can be either 'single' or 'album', indicating which type
    of file is being worked (album needs few extra steps). One kwarg,
    'album artist', passes extra tag field information for album mp3s.
    '''
    def tag_to_str(tag):
        '''Simple string cleaner'''
        if tag is None:
            return ''
        tag = str(tag)
        if tag == parsed.tag.title:
            if s.roman_to_arabic:
                tag = romantoarabic(tag)
        tag = tag.strip().lower()
        return tag

    if category == 'album' and not kwargs: (
        'For "album" category, you also need to pass album_artist keyword '
        'argument like so:\n tag_to_file(path/to/file, "album", '
        'album_artist="some string". Exiting...')

    file = re.search('(?<=[/])[^/]+$', filepath)[0]

    with NoStdErr():
        parsed = eyed3.load(filepath)
        date = str(tag_to_str(parsed.tag.getBestDate()))[:4]
    artist = tag_to_str(parsed.tag.artist)
    album  = tag_to_str(parsed.tag.album)
    title  = tag_to_str(parsed.tag.title)

	# Always a two-item tuple (track num, total tracks), Nones if
    # no data.
    if parsed.tag.track_num[0]:
        track_num = str(parsed.tag.track_num[0])
    else:
        try:
            track_num = re.search('\d\d?', file[:5])[0]
        except (IndexError, TypeError):
            track_num = ''

    if re.search(s.feat_rgx, artist):
        artist = re.sub(s.feat_rgx, ',', artist)

    if re.search(s.feat_rgx, title):
        extra_artists = re.search(f'{s.feat_rgx}.+', title)[0]
        extra_artists = re.sub(s.feat_rgx, '', extra_artists)
        extra_artists = extra_artists.rstrip(']) ')
        extra_artists = extra_artists.replace(', ', ',')
        title         = re.sub(f'{s.feat_rgx}.+$', '', title)
        artist        = artist + ',' + extra_artists

    if category == 'album' and not artist_has_comma:
        artist = artist.replace(', ', ',')
    ep_pre_rgx = ' [\(\[]?[Ee][Pp][\\)\]]?$'

    if category == 'album' and re.search(ep_pre_rgx, album):
        album = re.sub(ep_pre_rgx, '', album)

    if s.ep_eval:
        ep_conditions = (category == 'album'
                         and album_time < s.ep_max_length
                         and not re.search(r'\b[Ee][Pp]\b(?=[^\.])', album))
        if ep_conditions:
            album = f'{album} EP'

    title = re.sub('"', '\'', title)

    stripe = (f'  artist: "{artist}"\n'
			  f'  album: "{album}"\n'
			  f'  title: "{title}"\n'
			  f'  date: "{date}"\n'
			  f'  track no: "{track_num}"\n'
			  f'  path: "{filepath}"\n')
    if 'album_artist' in kwargs:
        a_artist = kwargs["album_artist"]
        a_artist = a_artist.strip().lower()
        stripe = f'  album artist: \"{a_artist}\"\n' + stripe

    with open(s.tag_changes_file, 'a+') as f:
        f.write(f'-\n{stripe}')


def romantoarabic(title):
    '''Converts low Roman numeral strings to Arabic numeral stirngs.'''
    romans = {'XX':'20', 'XIX':'19', '18':'XVIII', 'XVII':'17', 'XVI':'16', 
    		  'XV:':'15:', 'XV':'15', 'XIV:':'14:', 'XIV':'14', 'XIII:':'13:',
    		  'XIII':'13', 'XII:':'12:', 'XII':'12', 'XI:':'9:', 'XI':'9',
    		  ' X ': ' 10 ', 'IX:':'9:', 'IX':'9', 'VIII:':'8:', 'VIII':'8',
    		  'VII:':'7:', 'VII':'7', 'VI:':'6:', 'VI':'6', ' V ':' 5 ',
    		  'IV:':'4:', 'IV':'4', 'V:':'5:', 'III:':'3:', 'III':'3',
    		  'II:':'2:', 'II':'2'}

    for roman in romans:
        if roman in title:
            title = re.sub(roman, romans[roman], title)

    title = re.sub(" V$", " 5", title)
    return title


def nlp_capitalize(title):
    '''
    The Chicago Manual of Style capitalization instructions for Spacy.

    Titlechaser was stripped and converted into a function for purposes
    of this program. Below is its original address:
    https://github.com/tummychow/titlechaser
    '''
    title = str(title)
    title = title.replace('\\', '/')

    TO_CAPITALIZE = {'NN','NNS','NNP','NNPS','PRP','PRP$','WP','WP$','JJ',
    				 'JJR','JJS','MD','VB','VBD','VBG','VBN','VBP','VBZ','RB',
    				 'RBR','RBS','RP','WRB'}

    def capitalize_token(arg, idx):
        tok = arg[idx]
        return (
            (idx == 0 or idx == len(arg)-1) or
            (tok.tag_ in TO_CAPITALIZE) or
            (tok.tag_ == 'IN' and tok.dep_ in {'mark', 'complm'}) or
            (idx > 0 and idx < len(arg)-1 and arg[idx+1].tag_ == 'HYPH'
              and arg[idx-1].tag_ != 'HYPH'))

    def titlecase_tokens(arg):
        ret = []
        for idx, tok in enumerate(arg):
            ret.append(tok.orth_.capitalize() if capitalize_token(arg, idx)
                       else tok.orth_)
            ret.append(tok.whitespace_)
        return ret

    nlp    = spacy.load('en')
    output = titlecase_tokens(nlp(title))
    title  = ''.join(output)
    return title


def rename_img(dir_path, filename, replace_with):
    rgx_search        = "^.+(?=(?:.jpg|.png))"
    renamed_file      = re.sub(rgx_search, replace_with, filename)
    renamed_file_path = f'{dir_path}/{renamed_file}'
    renames(f'{dir_path}/{filename}', renamed_file_path)



# Startup actions:
# * checks if important fields are properly set in settings.py
# * run mp3val if enabled
# * verifies if any blacklisted program is running, prevents running
#   if so
# * prepares files and directories for operations
print('MP3 Cleaner started, reading files...')

if not all([s.base_dir, s.dest_dir, s.tag_changes_file, s.feat_rgx]) or \
   not any([s.write_to_v1, s.write_to_v2]):
    print('Please fill all the "file settings" fields in settings.py before '
          'running this program')
    sys.exit()

if s.app_blacklist:
    for app in s.app_blacklist:
        check = popen(f'ps aux | grep -i {app} | grep -v grep | wc -l')
        check = check.read().strip()
        check = int(check)

        if check:
            raise ValueError(
              f'Please close {app} first before running the program. '
              'Exiting...')

makedirs(f'{s.base_dir}/{s.broken_dir}', exist_ok=True)
with open(s.tag_changes_file, 'w') as f:
    f.write('')


# Move non-mp3 albums to notmp3_dir
dirs = [d for d in listdir(s.base_dir) if d != s.broken_dir and
                                          d != s.notmp3_dir]


def glob_notmp3(d):
    notmp3_files = []
    notmp3_formats = ['aac', 'aiff', 'alac', 'ape', 'flac', 'mpc', 'ogg', 'opus', 'wav', 'wma']  
    for ext in notmp3_formats:
        notmp3_files.extend(glob(f'{s.base_dir}/{d}/**/*.{ext}', recursive=True))
    return notmp3_files

for d in dirs:
    dir_path = f'{s.base_dir}/{d}'
    notmp3_files = glob_notmp3(d)
    if notmp3_files:
        print(f'"{d}" directory contains flac files, moving it to '
              f'"{s.notmp3_dir}" directory')
        renames(dir_path, f'{s.base_dir}/{s.notmp3_dir}/{d}')


# Test/repair all mp3 files, move broken, delete junk files
base_dir_slashes = s.base_dir.count('/')

all_items = glob(f'{s.base_dir}/**/*', recursive=True) 
all_files = [f for f in all_items if path.isfile(f)]
mp3_files = [a for a in all_files if a[-4:] == '.mp3']
jnk_files = [j for j in all_files if j[-4:] != '.jpeg' and
                                     j[-4:] != '.jpg' and
                                     j[-4:] != '.mp3' and
                                     j[-4:] != '.png']

for jnk_file in jnk_files:
    remove(jnk_file)

if s.enable_mp3val:
    print('mp3val enabled, fixing errors in files...')

for mp3_path in mp3_files:
    if s.enable_mp3val:
        run(['mp3val', '-f', '-nb', mp3_path], stdout=DEVNULL, stderr=DEVNULL)

    with NoStdErr():
        parsed = eyed3.load(mp3_path)

    if not parsed:
        print((f'file {mp3_path} is broken, moving it to "{s.broken_dir}" '
                'subdirectory'))
        mp3_path_slashes = mp3_path.count('/')

        if mp3_path_slashes   == base_dir_slashes + 1:  # single
            renames(mp3_path, f'{s.base_dir}/{s.broken_dir}/')

        elif mp3_path_slashes == base_dir_slashes + 2:  # album
            dir_of_file = '/'.join(mp3_path.split('/')[-2:-1])
            filename    = mp3_path.split('/')[-1]
            renames(f'{s.base_dir}/{dir_of_file}/{filename}',
                    f'{s.base_dir}/{s.broken_dir}/{dir_of_file}/{filename}')


curr_file        = 0
total_n_of_files = eval_total_files()
files            = [name for name in listdir(s.base_dir)
                    if not path.isdir(path.join(s.base_dir, name))]
dirs             = [name for name in listdir(s.base_dir)
                    if path.isdir(path.join(s.base_dir, name))
                    and name != s.broken_dir
                    and name != s.notmp3_dir]


# Rename mp3 subdirs to enumerated CD dirs, move relevant imgs from
# subdirs to album dir, delete everything else
for d in dirs:
    subdirs = [name for name in listdir(f'{s.base_dir}/{d}')
               if path.isdir(path.join(f'{s.base_dir}/{d}', name))]

    cd_num = 0
    for sub in subdirs:
        sub_path        = f'{s.base_dir}/{d}/{sub}'
        sub_parent_path = f'{s.base_dir}/{d}'
        subdir_mp3s   = glob(f'{sub_path}/*.mp3')
        subdir_imgs   = glob(f'{sub_path}/*.jpg') + glob(f'{sub_path}/*.png')
        
        if subdir_mp3s:
            cd_num += 1
            last_slash = sub_path.rfind('/')
            cdp = f'{sub_path[:last_slash]} {sub_path[last_slash+1:]}.CD{cd_num}'
            renames(sub_path, cdp)
            dir_content = glob(f'{sub_parent_path}/*')
            if not dir_content:
                rmdir(sub_parent_path)

        elif subdir_imgs:
            for i in subdir_imgs:
                filename = i.split('/')[-1]
                renames(i, f'{sub_parent_path}/{filename}')

        elif not subdir_mp3s and not subdir_imgs:
            rmdir(sub_path)

dirs = [name for name in listdir(s.base_dir)
        if path.isdir(path.join(s.base_dir, name))
        and name != s.broken_dir
        and name != s.notmp3_dir]


# Tags to yaml file, directory level operations
for file in files:
    report_current(file)
    tag_to_file(f'{s.base_dir}/{file}')


for d in dirs:
    dir_path  = f'{s.base_dir}/{d}'
    dir_files = listdir(f'{dir_path}')

    mp3_files = [f for f in dir_files if f.split('.')[-1] == 'mp3']
    if not mp3_files:
        print(f'folder "{d}" does not contain any mp3 files, skipping')
        continue

    artist_tags      = []
    album_time       = 0
    artist_has_comma = False


    # First full iteration: calculate album length, gather artist names
    for file in mp3_files:
        full_path = f'{dir_path}/{file}'

        with NoStdErr():
            parsed = eyed3.load(full_path)

        if s.ep_eval:
            album_time += parsed.info.time_secs
            artist_tags.append(str(parsed.tag.artist))
    
    artist_tags.sort(key=len)

    if ', ' in artist_tags[0]:
        artist_has_comma = True


    # Second interation: correct tags
    for file in mp3_files:
        report_current(file)
        full_path = f'{dir_path}/{file}'
        tag_to_file(full_path, 'album', album_artist=artist_tags[0])


    # Sort out folder images
    for f in dir_files:
        if '.jpeg' in f:
            src_path     = f'{dir_path}/{f}'
            new_filename = re.sub('\.jpeg', '.jpg', f)
            dest_path    = f'{dir_path}/{new_filename}'
            renames(src_path, dest_path)

    dir_imgs     = [name for name in listdir(f'{dir_path}')
                    if '.jpg' in name or '.png' in name]
    img_iter     = 0
    front_exists = False
    back_exists  = False

    for f in dir_imgs:
        report_current(f)
        f_path = f'{dir_path}/{f}'

        file_size = path.getsize(f_path)
        if file_size < s.img_min_size:
            print(f' {f} file size is too small, deleting...')
            remove(f_path)
            continue

        if s.img_conv_compr:
            if '.jpg' in f:
                c_rate = run(['identify', '-format', '%Q', f_path],
                             stdout=PIPE).stdout
                c_rate = int(c_rate)
                if c_rate == 100:
                    run(['jpegoptim', f'-m{s.jpg_compr_lvl}', f_path],
                    stdout=DEVNULL)

            if '.png' in f:
                run(['mogrify', '-format', 'jpg', '-quality', '100', f_path],
                    stdout=DEVNULL)
                remove(f_path)
                f = re.sub('\.png', '.jpg', f)
                f_path = f'{dir_path}/{f}'

                run(['jpegoptim',
                     f'-m{s.jpg_compr_lvl}',
                     f_path],
                    stdout=DEVNULL)

        if len(dir_imgs) == 1 and f != 'front.jpg':
            rename_img(dir_path, f, 'front')
            front_exists = True

        else:
            if not front_exists and ('front' in f or 'folder' in f):
                rename_img(dir_path, f, 'front')
                front_exists = True

            elif not back_exists and 'back' in f:
                rename_img(dir_path, f, 'back')
                back_exists = True

            else:
                img_iter      +=1
                img_iter_final = (f'0{img_iter}' if len(str(img_iter)) == 1
                                  else img_iter)
                rename_img(dir_path, f, f"album-art-{img_iter_final}")

    dir_jpgs = [f'{dir_path}/{name}' for name in listdir(f'{dir_path}')
                if '.jpg' in name]
    for j in dir_jpgs:
        stripe = f'-\n  path: "{j}"\n'
        with open(s.tag_changes_file, 'a') as f:
            f.write(stripe)



# Correct tags file:
# * reads file containing freshly-fetched tag information
# * extracts just the tag data from yaml
# * runs a series of string corrections on it
# * glues it to the remainder of that yaml file
# * saves to a file and prompts user to edit it
curr_file = 0
with open(s.tag_changes_file) as f:
    tags_file = f.read().splitlines()

keys = []
vals = []
for t in tags_file:
    if s.base_dir in t or t == '-':
        keys.append(t)
        vals.append('')
    else:
        keys.append(t.split(': ')[0])
        vals.append(t.split(': ', 1)[1])

tag_string = '\n'.join(vals)

if s.enable_nlp:
    tag_string = nlp_capitalize(tag_string)
else:
    tag_string = tag_string.title()


regexes = {
    'AiN\'t':                                      'Ain\'t',
    r'(?<=\d)Am(?=\b)':                            'AM',    
    'dN\'t':                                       'dn\'t',
    'DoN\'t':                                      'Don\'t',
    r'\bEp\b(?=[^\.])':                            'EP',
    r'\bMc\b':                                     'MC',
    r'(?<=\d)Pm(?=\b)':                            'PM',
}


if s.del_bonus_track:
    regexes[' ?[\[\(] ?[Bb]onus [Tt]rack ?[\]\)]']      = ''

if s.del_explicit:
    regexes[' ?[\[\(] ?[Ee]xplicit ?[\]\)]']            = ''

if s.del_lp:
    regexes[r' ?[\(\[]?\b[Ll][Pp]\b ?[\)\]]?']          = ''

if s.del_orig_mix:
    regexes[' ?[\[\(] ?[Oo]riginal [Mm]ix ?[\]\)]']     = ''

if s.del_produced:
    regexes[' ?[\(\[] ?[Pp]rod(?:\.|uced)(?: [Bb]y|)'
    '[^\)\]\n]+ ?[\)\]]']                               = ''


if s.chn_edit:
    regexes[' ?[\(\[] ?[Ee]dit ?[\)\]]']                = s.chn_edit

if s.chn_extended:
    regexes[' ?[\[\(] ?[Ee]xtended ?[\]\)]']            = s.chn_extended

if s.chn_extended_mix:
    regexes[' ?[\[\(]? ?[Ee]xtended [Mm]ix ?[\]\)]?']   = s.chn_extended_mix

if s.chn_instrumental:
    regexes[' ?[\[\(] ?[Ii]nstr(?:\.|umental) ?[\]\)]'] = s.chn_instrumental

if s.chn_live:
    regexes[' ?[\(\[] ?[Ll]ive ?[\)\]]']                = s.chn_live

if s.chn_mix:
    regexes[' ?[\[\(] ?(.+) [Mm]ix ?[\]\)]']            = s.chn_mix

if s.chn_ost:
    regexes[' Ost']                                     = s.chn_ost

if s.chn_orig_sdtrack:
    regexes[' ?[\[\(]? ?(?:[Oo]riginal )(?:[Mm]ovie |)'
    '(?:[Mm]otion |)(?:[Pp]icture |)[Ss]oundtrack'
    ' ?(?:[Aa]lbum|)[\]\)]?']                           = s.chn_orig_sdtrack

if s.chn_cover:
    regexes['[\[\(] ?(\w+) Cover ?[\]\)]']              = s.chn_cover

if s.chn_remix:
    regexes['[Rr]emix']                                 = s.chn_remix

if s.chn_remix2:
    regexes[' ?[\[\(] ?[Rr]emix ?[\]\)]']               = s.chn_remix2

if s.chn_remix3:
    regexes[' ?[\[\(] ?(.+) [Rr]emix ?[\]\)]']          = s.chn_remix3

if s.chn_reprise:
    regexes['[Rr]eprise']                               = s.chn_reprise

if s.chn_version:
    regexes[' ?[\(\[] ?(.+) [Vv]ersion ?[\)\]]']        = s.chn_version

regexes[' {2,}']                                        = ' '



for key, val in regexes.items():
    tag_string = re.sub(key, val, tag_string)

tag_string = re.sub('("\w)', lambda m: m.group(1).upper(), tag_string)

vals = tag_string.split('\n')

tags_file = ''
for key,val in zip(keys,vals):
    if val:
        tags_file += f'{key}: {val}\n'
    else:
        tags_file += f'{key}\n'

with open(s.tag_changes_file, 'w') as f:
    f.write(tags_file.strip())


if s.text_editor:
    run([s.text_editor, s.tag_changes_file])
    input('\nFinished correcting the file? Press ENTER...')



# Save tags, move files:
# * read and parse the yaml tag data file
# * parse mp3 files and save tags to them
# * set up directory and filenames based on tag data
# * rename files, move them to newly-created directories
print('\nSaving tags, moving files...')
total_n_of_files = eval_total_files()
yaml_rgx = '(?<=").+(?=")'

with open(s.tag_changes_file) as f:
    tag_stripes = f.read().strip('-\s\n').split('\n-\n')

for t in tag_stripes:
    tag_stripe = t.split('\n')
    src_path   = re.search(yaml_rgx, tag_stripe[-1])[0]
    filename   = src_path.split('/')[-1]

    if len(tag_stripe) == 1:  # image
        report_current(filename)
        renames(src_path, f'{final_dir}/{filename}')
        continue

    with NoStdErr():
        parsed = eyed3.load(src_path)
    parsed.tag.clear()

    try:
        if len(tag_stripe) == 7:  # album
            parsed.tag.album_artist = re.search(yaml_rgx, tag_stripe[0])[0]
        parsed.tag.artist         = re.search(yaml_rgx, tag_stripe[-6])[0]
        parsed.tag.album          = re.search(yaml_rgx, tag_stripe[-5])[0]
        parsed.tag.title          = re.search(yaml_rgx, tag_stripe[-4])[0]
        parsed.tag.recording_date = re.search(yaml_rgx, tag_stripe[-3])[0]
        parsed.tag.track_num      = re.search(yaml_rgx, tag_stripe[-2])[0]
    except TypeError:
        print('Error: at least one tag field in file was left blank. '
              'Exiting...')
        sys.exit()

    with NoStdErr():
        if s.write_to_v1:
            parsed.tag.save(filename=src_path, version=(1,1,0))
        if s.write_to_v2:
            parsed.tag.save(filename=src_path, version=s.tag_v2_version)

    report_current(filename)

    parsed.tag.album = parsed.tag.album.replace('/',' # ').replace('  ', ' ')
    parsed.tag.title = parsed.tag.title.replace('/',' # ').replace('  ', ' ')

    if len(parsed.tag.title) > 80:
        parsed.tag.title = f'{parsed.tag.title[:80]}(...)'

    if len(tag_stripe) == 6:  # single track
        dest_name = f'{parsed.tag.artist} - {parsed.tag.title}.mp3'
        renames(src_path, f'{s.dest_dir}/{dest_name}')

    elif len(tag_stripe) == 7:
        t_no = str(parsed.tag.track_num[0])
        if len(t_no) == 1:
            t_no = f'0{t_no}'

        dest_name         = f'{t_no} {parsed.tag.title}.mp3'
        dest_album_folder = (f'{parsed.tag.album_artist} - '
        					 f'{parsed.tag.recording_date} - '
        					 f'{parsed.tag.album}')
        final_dir         = f'{s.dest_dir}/{dest_album_folder}'

        multiple_cd = re.search('\.CD\d', src_path)
        if multiple_cd:
            cd_num    = multiple_cd[0]
            cd_num    = cd_num[1:]
            final_dir = f'{s.dest_dir}/{dest_album_folder}/{cd_num}'

        renames(src_path, f'{final_dir}/{dest_name}')


# Remove remaining empty folders
dirs = [name for name in listdir(s.base_dir)
        if path.isdir(path.join(s.base_dir, name))]

for d in dirs:
    dir_path  = f'{s.base_dir}/{d}'
    dir_items = listdir(dir_path)

    if not dir_items:
        rmdir(dir_path)
