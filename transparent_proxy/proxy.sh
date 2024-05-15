#!/bin/bash

mitmproxy --mode transparent --certs *=servercert.pem --set client_certs=clientcert.pem

