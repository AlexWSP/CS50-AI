import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    file_contents = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            f = open(os.path.join(root, file), 'r', encoding='utf8')
            file_contents[file] = f.read()
    return file_contents

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.
    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    punctuation = string.punctuation
    stop_words = nltk.corpus.stopwords.words("english")

    words = nltk.word_tokenize(document.lower())
    
    words_list = []
    for word in words:
        if word not in punctuation and word not in stop_words:
            words_list.append(word)
    return words_list


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.
    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    IDFs = {}
    words = set()

    for i in documents.values():
        for word in i:
            words.add(word)

    for word in words:
        NumDocumentsContainingWord = 0
        for sentence in documents.values():
            if word in sentence:
                NumDocumentsContainingWord += 1

        idf = math.log(len(documents) / NumDocumentsContainingWord)
        IDFs[word] = idf
    
    return IDFs

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    file_scores = {}

    for file in files.keys():
        tf_idf = 0
        for word in query:
            count = 0
            for i in files[file]:
                if word == i:
                    count += 1
            tf_idf += count * idfs[word]
        file_scores[file] = tf_idf
        
    file_scores = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)

    topn_ranked_files = []
    for i in file_scores:
        topn_ranked_files.append(i[0])

    return topn_ranked_files[:n]

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_scores = {}

    for sentence in sentences.keys():
        idf = 0
        for word in query.intersection(sentences[sentence]):
            idf += idfs[word]

        words_in_sentencequery = sum(map(lambda x: x in query.intersection(sentences[sentence]), sentences[sentence]))            
        query_term_density = words_in_sentencequery / len(sentences[sentence])

        sentence_scores[sentence] = {'idf': idf, 'qtd': query_term_density}

    sentence_scores = sorted(sentence_scores.items(), key=lambda x: (x[1]['idf'], x[1]['qtd']), reverse=True)
    
    topn_ranked_sentences = []
    for i in sentence_scores:
        topn_ranked_sentences.append(i[0])
    
    return topn_ranked_sentences[:n]

if __name__ == "__main__":
    main()
