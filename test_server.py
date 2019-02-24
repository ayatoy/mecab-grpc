import signal
import subprocess
import time

import grpc

from mecab_pb2 import ParseRequest
from mecab_pb2_grpc import ParserStub


def test():
    proc = subprocess.Popen(['python', 'server.py'])
    time.sleep(3)

    sentences = [
        'すもももももももものうち',
        'にわにはにわにわとりがいる',
    ]

    with grpc.insecure_channel('localhost:50051') as channel:
        stub = ParserStub(channel)
        response = stub.Parse(ParseRequest(sentences=sentences, dictionary='ipadic'))
        assert len(sentences) == len(response.sentences)
        for s1, s2 in zip(sentences, response.sentences):
            assert s1 == ''.join([word.surface for word in s2.words])

    proc.send_signal(signal.SIGINT)
    proc.wait()

    assert 0 == proc.poll()

