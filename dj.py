#!/bin/python
import requests # to get our data
import json # might not be needed
import os # to make call to media player
import re # to match title
from html import unescape
import argparse
import subprocess


#for "help" output
boards = {
    "wsg" : "Worksafe Gif",
    "gif" : "Gif (NSFW)",
}

def getSearch():
    search = input("What would you like to search for?\n> ")
    return search

def getCatalog(board="wsg"):
    #get our data using 4chan API
    board_url = 'https://a.4cdn.org/%s/catalog.json' % (board)
    
    catalog = requests.get(board_url).json()
    #this is 10 items long, we need to extract thread names only.
    return catalog

def getContent(board, thread):
    content = []
    html = requests.get('https://boards.4chan.org/' + board + '/thread/' + thread) # get the thread's HTML body
    wf = '((https?)?:?(\\/\\/))?(([\\d*|\\w*]+\\.){2,}[\\w*]+\\/)([\\w*|\\d*]+\\/)*([\\w*|\\d*]*\\.(webm|mp4|mp3|avi|flv))' # grep for .webm URLS in 4chan HTML
    b_url = 'https://i.4cdn.org/' + board + '/'# base URL for webms (and all other content, but we want webms)
    r = re.findall(wf, html.text)
    for i in range(len(r)):
        url = b_url + r[i][6]
        if url not in content:
            content.append(url)

    return content

def stripHTML(string):
    #this is needed because 4chan stores HTML formatting in the JSON strings. Bleh.
    #I will eventually need to add some formatting (sub <br> for \n, etc.)
    br = re.compile('<br>')
    formatted = re.sub(br, '\n', string)
    cleanr = re.compile('<.*?>')
    cleanText = re.sub(cleanr, '', formatted)
    return cleanText

def cleanStr(string):
    #I'm doing too much in one print statement, let's refactor.
    #first let's fix the escaped HTML stuff
    unescaped = unescape(string)
    formatted = stripHTML(unescaped)
    return(formatted)

def getThreads(catalog, search_string="ygyl"):
    search = search_string.lower()
    results = {}
    i = 0
    for page in range(len(catalog)):
        for thread in range(len(catalog[page]['threads'])):
            thread_ = catalog[page]['threads'][thread]
            sub = thread_.get('sub') # get 'sub' if available
            com = thread_.get('com') # get 'com' if available
            no = thread_['no'] # get ID. This is always available.
            title = sub
            subTitle = com
            if sub is None:
                sub = ""
                title = com
                subTitle = ""
            if com is None:
                com = ""
                subTitle = ""
            if search in sub.lower() or search in com.lower():
                #print("found matching thread." + "\nTitle: " + cleanStr(sub) + "\nSub-Title: " + cleanStr(com) + "\nThread No: " + str(no) + '\n----------')
                results[str(no)] = {'title':cleanStr(title), 'subTitle':cleanStr(subTitle), 'no':str(no), 'replies':str(thread_['replies'])}

    return results


def handleSearch(results):
    if len(results) == 0:# when no GIF thread for your fetish exists
        print('nothing found')
        
    elif len(results) > 1:# if len == 1, go straight to output
        i = 0
        choices = {}
        print('Choose which thread you\'d like to use:\n')
        for result in results:#results from getThreads()
            print(str(i) + ') ' + str(results[result]['title']))
            if results[result]['subTitle'] != "":
                print(results[result]['subTitle'])
            print('Replies: ' + results[result]['replies'])
            print('-----')
            choices[i] = result
            i += 1
        choice = input('> ')
        try:
            return(choices[int(choice)])
        except:
            print('invalid number entered')
    else:
        for result in results:
            print('Using thread:\n')
            print(str(results[result]['title']))
            if results[result]['subTitle'] != "":
                print(results[result]['subTitle'])
            print('Replies: ' + results[result]['replies'])
            print('-------')
            return(result)


def plCreate(urls):
    pl = re.sub(',','',' '.join(urls))
    return pl
    #just making things look nicer

def mpv(urls, flag):
    try:
        command = "mpv %s %s" % (re.sub(',','',' '.join(urls)), flag)
        p = subprocess.Popen(command, shell=True)
        try:
            p.wait()
        except KeyboardInterrupt:
            p.terminate()
    except:
        pass

def writeOut(url, filename="dj.txt"):
    f = open(filename, 'w')
    f.write(url)
    f.close()


def run(query, board, output, flag):
    out = {
        'print' : print,
        'mpv' : mpv,
        'write' : writeOut
    }
    cat = getCatalog(board)
    r = getThreads(cat, query)
    thread = handleSearch(r)
    try:
        o = getContent(board, thread)
    except:
        return None

    if thread is not None:
        if output == 'write':
            out[output]('https://boards.4chan.org/' + str(board) + '/thread/' + thread)
        elif output == 'mpv':
           out[output](o, flag)
        else:
            out[output]('https://boards.4chan.org/' + str(board) + '/thread/' + thread)

# this is the part that handles command line input
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Thread you would like to search for", type=str)
    parser.add_argument("-b", "--board", nargs='?', const='wsg', default="wsg", help="specify board you would like to search", type=str)
    parser.add_argument('-o', '--output', nargs='?', const='print', default="mpv", type=str, help="specify the way you want dj to handle the results.")
    parser.add_argument('-f', '--flag', nargs='?', const="", type=str, help="Flag to pass to media player")
    args = parser.parse_args()
    
    run(args.query, args.board, args.output, args.flag)

if __name__ == '__main__':
    main()

