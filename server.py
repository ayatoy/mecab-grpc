from concurrent import futures
import os
import os.path
import subprocess
import threading
import time

import MeCab
import grpc

from mecab_pb2 import ParseResponse, Sentence, Word
from mecab_pb2_grpc import ParserServicer, add_ParserServicer_to_server

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

_HOST = os.environ.get('MECAB_GRPC_HOST', '[::]')
_PORT = os.environ.get('MECAB_GRPC_PORT', '50051')
_ADDRESS = _HOST + ':' + _PORT


class Environment:

    def __init__(self, default_dictionary='ipadic'):
        self.dictionary_directory = subprocess.check_output(['mecab-config', '--dicdir']).decode('utf-8').split('\n')[0]
        if not self.dictionary_directory:
            raise Exception('Invalid Directory: %r' % self.dictionary_directory)
        self.default_dictionary = default_dictionary
        self.dictionaries = set(os.listdir(self.dictionary_directory))
        self.taggers = threading.local()

    def get_tagger(self, dictionary):
        if dictionary not in self.dictionaries:
            dictionary = self.default_dictionary
        tagger = getattr(self.taggers, dictionary, None)
        if tagger is None:
            tagger = MeCab.Tagger('-d %s' % os.path.join(self.dictionary_directory, dictionary))
            # For bug that node.surface can not be obtained with Python3.
            tagger.parse('')
            setattr(self.taggers, dictionary, tagger)
        return tagger


class Parser(ParserServicer):

    def __init__(self, environment):
        self.environment = environment

    def Parse(self, request, context):
        sentence_texts = request.sentences
        dictionary = request.dictionary
        tagger = self.environment.get_tagger(dictionary)
        sentences = []
        for sentence_text in sentence_texts:
            words = []
            for row in tagger.parse(sentence_text).split('\n')[:-2]:
                cols = row.split('\t')
                words.append(Word(
                    surface=cols[0],
                    feature=cols[1].split(','),
                ))
            sentences.append(Sentence(words=words))
        return ParseResponse(sentences=sentences)


def serve():
    environment = Environment()
    server = grpc.server(futures.ThreadPoolExecutor())
    add_ParserServicer_to_server(Parser(environment), server)
    server.add_insecure_port(_ADDRESS)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
