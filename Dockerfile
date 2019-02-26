FROM python:3.5.6-alpine3.9
LABEL Name=mecab-grpc Version=1.0.0

RUN apk add --no-cache git make g++ swig

WORKDIR /
RUN git clone https://github.com/taku910/mecab.git
WORKDIR /mecab/mecab
RUN ./configure --enable-utf8-only \
    && make \
    && make check \
    && make install

WORKDIR /mecab/mecab-ipadic
RUN ./configure --with-charset=utf8 \
    && make \
    && make install

WORKDIR /mecab/mecab-jumandic
RUN ./configure --with-charset=utf8 \
    && make \
    && make install

COPY . /mecab-grpc
WORKDIR /mecab-grpc
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && sh protoc-gen.sh

CMD ["python", "server.py"]
