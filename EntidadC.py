# EntidadC.py

import cryptography.x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509 import Name, NameAttribute, CertificateBuilder
from cryptography.x509.oid import NameOID
import datetime
import os

def Crear_Base():
    ca_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Crear un certificado para la CA
    ca_subject = Name([
        NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        NameAttribute(NameOID.ORGANIZATION_NAME, u"My CA Organization"),
        NameAttribute(NameOID.COMMON_NAME, u"myca.com"),
    ])

    ca_cert = CertificateBuilder()\
        .subject_name(ca_subject)\
        .issuer_name(ca_subject)\
        .public_key(ca_private_key.public_key())\
        .serial_number(cryptography.x509.random_serial_number())\
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))\
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))\
        .add_extension(
            cryptography.x509.BasicConstraints(ca=True, path_length=None), critical=True
        )\
        .sign(ca_private_key, hashes.SHA256(), default_backend())

    with open("ca_private_key.pem", "wb") as f:
        f.write(ca_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open("ca_certificate.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    print("CA creada.")
    return ca_private_key, ca_cert
def Crear(ca_cert, clave_privada, cert_name):
    cert_path = os.path.join(os.getcwd(), cert_name)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    subject = Name([
        NameAttribute(NameOID.COUNTRY_NAME, u"CO"),
        NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Bogota"),
        NameAttribute(NameOID.LOCALITY_NAME, u"Bogota"),
        NameAttribute(NameOID.ORGANIZATION_NAME, u"Andes"),
        NameAttribute(NameOID.COMMON_NAME, u"Andes.com"),
    ])
    issuer = ca_cert.subject 

    cert = CertificateBuilder()\
        .subject_name(subject)\
        .issuer_name(issuer)\
        .public_key(private_key.public_key())\
        .serial_number(cryptography.x509.random_serial_number())\
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))\
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))\
        .add_extension(
            cryptography.x509.BasicConstraints(ca=False, path_length=None), critical=True
        )\
        .sign(clave_privada, hashes.SHA256(), default_backend())

    with open(cert_name, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Certificado y clave privada generados en: {cert_path}")

def Validar(cert_prueba, cert_base):
    with open(cert_prueba, "rb") as cert_file:
        server_cert = cryptography.x509.load_pem_x509_certificate(cert_file.read(), default_backend())

    with open(cert_base, "rb") as ca_cert_file:
        ca_cert = cryptography.x509.load_pem_x509_certificate(ca_cert_file.read(), default_backend())

    ca_public_key = ca_cert.public_key()

    ca_public_key.verify(
        server_cert.signature,
        server_cert.tbs_certificate_bytes,
        padding.PKCS1v15(),
        server_cert.signature_hash_algorithm
    )
    print("El certificado es válido.")

try:
    with open("ca_certificate.pem", "rb") as cert_file:
            cert_data = cert_file.read()
    cert_base = cryptography.x509.load_pem_x509_certificate(cert_data, default_backend())
    with open("ca_private_key.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None 
            )
    llave = private_key
except:
    llave, cert_base = Crear_Base()
Crear(cert_base,llave,"Certificado2.pem")
Validar("Certificado2.pem","ca_certificate.pem")