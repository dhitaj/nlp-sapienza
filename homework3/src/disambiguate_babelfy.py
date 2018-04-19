import urllib2
import urllib
import json
import gzip

from StringIO import StringIO

service_url = 'https://babelfy.io/v1/disambiguate'
lang = 'EN'
key  = ''

filehandle = open('triples/triples2.tsv') # the triples and the sentences where the triples were extracted
filehandle_write = open('triples/disambiguated_triples_sentence.tsv', 'a')

for line in filehandle:
    splitted = line.split('|')
    concept1 = splitted[0].strip()
    relation = splitted[1].strip()
    concept2 = splitted[2].strip()
    sentence = splitted[3].strip()
    if concept1 not in sentence:
        # I do this for the triples extracted where the concept might not be in the sentence but that sentence refers to the concept
        text = concept1+" "+sentence
    else:
        text = sentence
    babelnetid1 = -1
    babelnetid2 = -1
    params = {
    'text' : text,
    'lang' : lang,
    'key'  : key
    }

    url = service_url + '?' + urllib.urlencode(params)
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(request)

    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( response.read())
        f = gzip.GzipFile(fileobj=buf)
        data = json.loads(f.read())
        # retrieving data
        for result in data:
            charFragment = result.get('charFragment')
            cfStart = charFragment.get('start')
            cfEnd = charFragment.get('end')
            word = text[cfStart:cfEnd+1]
            print(word)
            synsetId = result.get('babelSynsetID')
            to_lower = word.lower()
            if to_lower.startswith(concept1.lower()):
                babelnetid1 = synsetId
            if to_lower.startswith(concept2.lower()):
                babelnetid2 = synsetId

            print synsetId

    filehandle_write.write(concept1 + " | " + relation + " | " + concept2 + " | " + sentence+" | " + concept1+" | "+str(babelnetid1)+" | "+concept2+" | "+str(babelnetid2))
    filehandle_write.write('\n')
