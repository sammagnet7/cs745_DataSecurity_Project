openssl genrsa -out server-a-selfsigned.key 2048
sleep 1
openssl req -new -key server-a-selfsigned.key -out server-a-selfsigned.csr < input.txt
sleep 1
openssl x509 -req -in server-a-selfsigned.csr -signkey server-a-selfsigned.key -out server-a-selfsigned.crt
