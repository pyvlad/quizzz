#!/bin/bash

# configure paths and file names
SSL_DIR=./playbooks/templates/staging/.ssl
SLUG="ssl"
KEY_PROTECTED="${SLUG}-protected.key"
KEY_FINAL="${SLUG}.key"
CSR="${SLUG}.csr"
CERTIFICATE="${SLUG}.crt"

# 0. cd to SSL directory
mkdir -p $SSL_DIR
cd $SSL_DIR

# 1. write a private key using a 4096 bit key
openssl genrsa -des3 -out $KEY_PROTECTED 4096
# enter pass phrase here
# recreate the key file but whithout the pass phrase
openssl rsa -in $KEY_PROTECTED -out $KEY_FINAL

# 2. create CSR (a Certificate Signing Request)
openssl req -new -key $KEY_FINAL -out $CSR
# fill in all the requested information here

# 3. this is our final certificate with lifetime of 730 days
openssl x509 -req -days 730 -in $CSR -signkey $KEY_FINAL -out $CERTIFICATE

# 4. remove interim files
rm $KEY_PROTECTED
rm $CSR