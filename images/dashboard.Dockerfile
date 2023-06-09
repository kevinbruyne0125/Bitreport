FROM ruby:2.6.1

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update -qq && \
    apt-get install -y \
        build-essential \
        curl \
        gnuplot \
        libcairo2-dev \
        libpq-dev \
        nano \
        nodejs \
        libxml2-dev \
        libfftw3-dev \
        libmagickwand-dev \
        libopenexr-dev \
        liborc-0.4-0 \
        gobject-introspection \
        libgsf-1-dev \
        libglib2.0-dev \
        libexpat1-dev \
        liborc-0.4-dev \
        libpng-dev \
        libpango1.0-dev \
        automake \
        libtool \
        swig \
        gtk-doc-tools \
        yarn && \
    apt-get autoremove -y && \
    apt-get clean -y

RUN curl -s -L https://github.com/libvips/libvips/releases/download/v8.7.0/vips-8.7.0.tar.gz | tar -xz && \
    cd vips-8.7.0 && \
    ./configure && \
    make && \
    make install && \
    cd ~ && \
    rm -rf vips-8.7.0
