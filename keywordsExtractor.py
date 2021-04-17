'''
This script expects as input the directory containing all txt files generated by pytesseract
and extract key words and key phrases using rake_nltk
then generate metadata for each document and index  them in elasticsearch
'''

from rake_nltk import Rake
import sys
import os
from os import path
import logging
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from elasticsearch import Elasticsearch



#method to test if folder exists
def folder_exists(absolute_path):
    return path.exists(absolute_path) and path.isdir(absolute_path)
    
def exit_program_with_error (err_message):
    logging.error(err_message)
    logging.info('exiting the program ...')
    exit(1)

#this method extract the top 5 most frequent words from text . those words will be used as tag 
def top5words(text):
    nltk.download('stopwords')
    tokens = word_tokenize(text)
    #we  remove stopwords using nltk 
    filtered_tokenks= [word for word in tokens if not word in stopwords.words()]

    atlest4charToken = [token for token in filtered_tokenks if len(token)>=4 ]
    #we find the most frequent words excluding stop words
    wordfrecs = Counter(atlest4charToken)
    top5 = wordfrecs.most_common(5)
    tags = [top[0] for top in top5 ]
    return tags

# this method is called to post metada in elasticsearch
def storeMetadata(body):
    '''
    create elasticsearch connection with your elasticsearc url
    es = Elasticsearch(
            ['your_elasticsearch_host1', 'your_elasticsearch_host2', ... ],
            http_auth=('YOUR_USERNAME', 'YOUR_PASSWORD'),
            port=10202,
    )

    then index document
    es.index(index='documents', doc_type='post', id=1, body=  )
    '''
    print("indexing document")
  


def main():
    if len(sys.argv) < 2:
        exit_program_with_error("you must specify the txt file directory")

    txtDir = sys.argv[1]
    if not folder_exists(txtDir)  :
        exit_program_with_error("the specified directory : "+ txtDir +"does no exist")

    #for this example we support only txt files     
    supported_ext = ['.txt']
    files = os.listdir(txtDir)
    supported_files = [file  for file in files if ( not os.path.isdir(file) and len(os.path.splitext(file)) == 2 and os.path.splitext(file)[1] in supported_ext )]
    
    for supported_file in supported_files:
        full_path = os.path.join(txtDir,supported_file)
        f = open(full_path, 'r')
        text = f.read()
        rake = Rake()
        rake.extract_keywords_from_text(text)
        topPhrases = rake.get_ranked_phrases()
        document_content = ' '.join(topPhrases)
        #print(corpus)
        tags = top5words(document_content)
        #we can now index this document in elasticsearch
        metadataDoc = {"doc_name": supported_file, "content" : document_content, "tags" : tags}
        storeMetadata(metadataDoc)

        f.close()
        


if __name__ == "__main__":
    main()