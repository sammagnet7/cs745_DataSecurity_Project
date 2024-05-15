openssl x509 -req -in requests/client.csr -CA server-a-selfsigned.crt -CAkey server-a-selfsigned.key -CAcreateserial -out requests/client.crt -days 365
