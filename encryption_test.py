import base64
import os
from authlib.jose import JsonWebEncryption, jwt

# see also: https://github.com/lepture/authlib/blob/master/tests/jose/test_jwe.py

# 128 bit key to sign the JWT
jwt_key = bytes.fromhex("74738ff5536759589aee98fffdcd1876")
# create the JWT
jwt_header = {'alg': 'HS256'}
jwt_payload = {'iss': 'Authlib', 'sub': '123'}
jwt_encoded = jwt.encode(jwt_header, jwt_payload, jwt_key)

# 128 bit key to encrypt the JWT as JWE
jwe_key = bytes.fromhex("74738ff5536759589aee98fffdcd1876")
# create the JWE
jwe = JsonWebEncryption()
jwe_header = {'alg': 'A128KW', 'enc': 'A128CBC-HS256'}
jwe_payload = jwt_encoded
jwe_encrypted = jwe.serialize_compact(jwe_header, jwe_payload, jwe_key)
print(jwe_encrypted.decode('utf-8'))

# decrypt the JWE
data = jwe.deserialize_compact(jwe_encrypted, jwe_key)
jwe_header = data['header']
payload = data['payload']

# decode the JWT
claims = jwt.decode(payload, jwt_key)
print(claims)


