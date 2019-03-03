FROM python:3.5.6-alpine3.9
LABEL Name=mecab-grpc Version=1.0.0

COPY . /opt/mecab-grpc

RUN set -x \
    && apk add --no-cache --virtual .run-deps \
        g++ \
    \
    && apk add --no-cache --virtual .build-deps \
        git \
        make \
        swig \
    \
    && mkdir -p /usr/local/src \
    && cd /usr/local/src \
    && git clone https://github.com/taku910/mecab.git \
    \
    && cd /usr/local/src/mecab/mecab \
    && ./configure --enable-utf8-only && make && make check && make install \
    \
    && cd /usr/local/src/mecab/mecab-ipadic \
    && ./configure --with-charset=utf8 && make && make check && make install \
    \
    && cd /opt/mecab-grpc \
    && pip install \
        --disable-pip-version-check \
        --no-cache-dir \
        -r requirements.txt \
    && sh protoc-gen.sh \
    \
    && apk del --purge .build-deps \
    && rm -rf /usr/local/src/mecab

WORKDIR /opt/mecab-grpc
CMD ["python", "server.py"]
