import os
import sys
from lxml.builder import E
from lxml import etree
from guessit import guessit
import tmdbsimple


# CONFIG
video_types = ('.mkv', '.avi', '.mp4')
output_movies = 'Movies'
output_tvshows = 'TV Shows'
output_unknown = 'Unknown'

input = '/mnt/STORAGE'
output = '/mnt/DEV'
tmdbsimple.API_KEY = ''
    

def is_proper_media(media):
    return media.endswith(video_types) and \
           'SAMPLE' not in media.upper();

log = open(os.path.join(output, 'orgasmise.log'), 'a')

search = tmdbsimple.Search()
# TODO: for same tvshow dont rescan on tmdb
def magic(root, file, guess, again=False):
    # guessit sometimes leaves in dots for example:
    # The Lord Of The Rings: The Two Towers E.E.
    # And TMDB won't process it...
    guess['title'] = guess['title'].replace('.', ' ')

    # search on TMDB 
    # Could use search.multi but this yields less and thus more accurate
    if guess['type'] is 'movie':
        res = search.movie(query=guess['title'])
    else:
        res = search.tv(query=guess['title'])
    # TODO: try a search.multi and see if it yeilds any ?

    # if not found on TMDB
    if not len(res['results']):
        # .. but haven't retried yet, then retry with one word less
        # could be useful to get rid of unrecognized, non-standard editions
        # names like: Extended, Directors etc.
        if not again:
            guess['title'] = ' '.join(guess['title'].split()[:-1])
            return magic(root, file, guess, True)

        # .. otherwise classify as UNKNOWN
        fp = os.path.join(output, output_unknown)
        if not os.path.isdir(fp):
            os.mkdir(fp)

        fp = os.path.join(fp, file)
        try:
            os.symlink(os.path.join(root,file), fp)
        except Exception as e:
            print("ERROR: " + str(e))

        thrash = log.write('UNKNOWN' + ';' + \
            os.path.join(root,file) + ';' + \
            guess['title'] + ';' \
            'N/A' + ';' + \
            fp + \
            '\n')
        return 'UNKNOWN'


    # TODO: choose best based on release date if available
    # EX: The Man ~ The Elephant Man
    best_match = res['results'][0]

    if guess['type'] is 'movie':
        m = best_match
        nfo = E.movie(
            E.title(m['title']),
            E.rating(str(m['vote_average'])),
            E.releasedate(str(m['release_date'])),
            #E.tagline(m['tagline']),
            E.plot(m['overview']),
            E.tmdbid(str(m['id'])),
            E.art(
                E.poster(m['poster_path']),
                E.fanart(m['backdrop_path'])
            )
        )



    if guess['type'] is 'movie':
        filename = best_match['title'] + ' (' + \
                   best_match['release_date'].split('-')[0] + ')'
    else:
        filename = best_match['name'] + ' (' + \
                   best_match['first_air_date'].split('-')[0] + ')'

    
    # Choose root folder based on media type
    if guess['type'] is 'movie':
        fp = os.path.join(output, output_movies)   
    else:
        fp = os.path.join(output, output_tvshows)
    if not os.path.isdir(fp):
        os.mkdir(fp)

    # Create individual folder for the media
    fp = os.path.join(fp, filename)
    if not os.path.isdir(fp):
        os.mkdir(fp)

    # Append the Season and Episode number for TV Shows' paths and names
    if guess['type'] is 'episode':
        if  'season' in guess:
            filename = filename + ' S' + str(guess['season']) 
            fp = os.path.join(fp, str(guess['season']))
            if not os.path.isdir(fp):
                os.mkdir(fp)
        filename = filename + 'E' + str(guess['episode'])


    # Create the final filename with the original container type
    fp = os.path.join(fp, filename)
    nfofp = fp + '.nfo'
    fp = fp + '.' + guess['container']

    thrash = log.write(
        guess['type'].upper() + ';' + \
        os.path.join(root,file) + ';' + \
        guess['title'] + ';' + \
        filename + ';' + \
        fp + \
        '\n')

    # TODO: more actions like SYMLINK, COPY, MOVE, etc..
    try:
        os.symlink(
            os.path.abspath(os.path.join(input, os.path.join(root,file))),
            os.path.abspath(fp))
        #if nfo:
        #    with open(nfofp, 'w') as f:
        #        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
        #        f.write(str(etree.tostring(nfo, pretty_print=True), 'utf-8'))
        #        f.close()
    except Exception as e:
        print("ERROR: " + str(e))


def orgasmise():
    os.chdir(input)

    for root, directories, files in os.walk('.'):
        for file in files:
            full = os.path.join(root, file)
            if is_proper_media(file):                
                print('PROC: ' + full)
                guess = guessit(full)
                magic(root, file, guess)
            else:
                print('SKIP: ' + full)

