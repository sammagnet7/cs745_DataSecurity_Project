openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr < input.txt
