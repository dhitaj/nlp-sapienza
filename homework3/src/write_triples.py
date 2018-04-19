__author__ = 'dorjan hitaj'

filehandle = open('triples/triples_sentences.tsv')
filehandle_triples = open('triples/triples.tsv', 'a')

shape = 0
color = 0
activity = 0
similarity = 0
howToUse = 0
for line in filehandle:
    splitted = line.split("|")
    if len(splitted)>1:
        concept = splitted[0]
        print(concept)

        if splitted[1].strip() == 'shape':
            shape+=1
            filehandle_triples.write("{}\t{}\t{}".format(concept.strip(), splitted[1].strip(), splitted[2].strip()))
            filehandle_triples.write("\n")
        elif splitted[1].strip() == 'colorPattern':
            color+=1
            filehandle_triples.write("{}\t{}\t{}".format(concept.strip(), splitted[1].strip(), splitted[2].strip()))
            filehandle_triples.write("\n")
        elif splitted[1].strip() == 'similarity':
            similarity+=1
            filehandle_triples.write("{}\t{}\t{}".format(concept.strip(), splitted[1].strip(), splitted[2].strip()))
            filehandle_triples.write("\n")
        elif splitted[1].strip() == 'activity':
            activity+=1
            filehandle_triples.write("{}\t{}\t{}".format(concept.strip(), splitted[1].strip(), splitted[2].strip()))
            filehandle_triples.write("\n")
        elif splitted[1].strip() == 'howToUse':
            howToUse+=1
            filehandle_triples.write("{}\t{}\t{}".format(concept.strip(), splitted[1].strip(), splitted[2].strip()))
            filehandle_triples.write("\n")

print(shape, color, similarity, activity, howToUse)
