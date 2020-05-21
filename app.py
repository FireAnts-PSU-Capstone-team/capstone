from flask import Flask, Response, jsonify, make_response, request, session
import ssl
import os.path
import re
import ssl
from kanabi.configure import create_app

app = create_app()


if __name__ == "__main__":
    # Generating Server Certificates:
    # Creating a Certificate Authority that will validate certificates. Creates 'ca.key' and 'ca-crt.pem' files.
    #   $ openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    # Create server private key and CSR (Certificate Signing Request) Creates 'server.csr' and 'server.key' files.
    #    $ openssl req -nodes -new -keyout server.key -out server.csr
    # Generate certificate from CSR using root certificate and CA private key. Creates 'server.crt' and 'ca-crt.srl' files.
    #   $ openssl x509 -req -days 365 -in server.csr -CA ca-crt.pem -CAkey ca.key -CAcreateserial -out server.crt
    # Verification of certificates can be performed using the following command:
    #   $ openssl verify -CAfile ca-crt.pem server.crt

    # Generating Client Certificates:
    # Create a client private key and server CSR (Certificate Signing Request). Creates 'client.csr' and 'client.key' files.
    #   $ openssl req -nodes -new -keyout client.key -out client.csr
    # Generate certificate from CSR using root CA certificate and CA private key. Creates 'client.crt' file.
    #   $ openssl x509 -req -days 365 -in client.csr -CA ca-crt.pem -CAkey ca.key -CAcreateserial -out client.crt
    # Verification of certificates can be performed using the following command:
    #   $ openssl verify -CAfile ca-crt.pem client.crt
    # Packages 'client.crt' and 'client.key' files into .p12 format for importing into chrome/firefox etc.
    #   $ openssl pkcs12 -export -in client.crt -inkey client.key -out client.p12

    # To properly test Client-Side SSL using Certificate-based authentication:
    # Testing the fail case where we have not provided the certificate:
    #   $ curl --insecure https://DOMAIN_NAME:PORT/RESOURCE_PATH/RESOURCE
    #   OUTPUT: curl: (35) gnutls_handshake() failed: Handshake failed
    # Testing the fail case where we provided the certificate but our request is over http not https:
    #   $ curl --insecure --cacert ca-crt.pem --key client.key --cert client.crt http://DOMAIN:PORT/RESOURCE_PATH/RESOURCE
    #   OUTPUT: curl: (52) Empty reply from server
    #   NOTE: the insecure flag is used to bypass curl verifying the self-signed certificate is from a trusted cert authority.
    # Testing the successful case where we provided the certificate and our request is over https.
    #   $ curl --insecure --cacert ca-crt.pem --key client.key --cert client.crt https://DOMAIN:PORT/RESOURCE_PATH/RESOURCE
    #   OUTPUT: (returns expected result)

    #context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    #context.verify_mode = ssl.CERT_REQUIRED          # Not sure about this. Maybe depricated and removed? Need to verify it's working or stick with Connor's
    #context.load_verify_locations('kanabi/certs/ca-crt.pem')
    #context.load_cert_chain('kanabi/certs/server.crt', 'kanabi/certs/server.key')
    #app.run(debug=True, host='127.0.0.1', port=443, ssl_context=context)

    context = ('./kanabi/configs/cert.pem', './kanabi/configs/key.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=True, debug=True)



