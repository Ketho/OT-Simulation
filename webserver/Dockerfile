FROM wordpress:5.8-php7.4-apache

# Install specific Bash version 3.1
RUN apt-get update && \
    apt-get install -y wget build-essential && \
    wget http://ftp.gnu.org/gnu/bash/bash-3.1.tar.gz && \
    tar -xzf bash-3.1.tar.gz && \
    cd bash-3.1 && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf bash-3.1 bash-3.1.tar.gz
    
RUN a2enmod cgi

COPY vulnerable.sh /usr/lib/cgi-bin/vulnerable.sh

COPY passwords.txt /

RUN chmod +rx /usr/lib/cgi-bin/vulnerable.sh
    chmod -r /passwords.txt

# Expose WordPress on port 80
EXPOSE 80
