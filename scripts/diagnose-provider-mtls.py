"""Diagnose Windows provider AutoMTLS without weakening certificate verification.

No Terraform/provider configuration RPC or AWS call is sent. Prints booleans/status
only; ephemeral certificates/private keys stay in an ignored temporary directory
and are removed on exit. Requires cryptography and PyOpenSSL in the chosen Python.
"""
import argparse
import base64
import datetime
import hashlib
import ipaddress
import json
import os
import pathlib
import queue
import select
import socket
import ssl
import subprocess
import tempfile
import threading
import time
import zipfile


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', type=pathlib.Path, default=pathlib.Path('infra/site/.terraform/providers/registry.terraform.io/hashicorp/aws/6.74.0/windows_amd64/terraform-provider-aws_v6.74.0_x5.exe'))
    parser.add_argument('--archive', type=pathlib.Path, default=pathlib.Path('.tools/mirror/registry.terraform.io/hashicorp/aws/terraform-provider-aws_6.74.0_windows_amd64.zip'))
    parser.add_argument('--checksums', type=pathlib.Path, default=pathlib.Path('.tools/provider-checksums.txt'))
    return parser.parse_args()


def diagnose(args):
    from OpenSSL import SSL, crypto
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

    if os.name != 'nt':
        raise ValueError('This diagnostic targets the Windows TCP-loopback provider path')
    provider = args.provider.resolve(strict=True)
    archive = args.archive.resolve(strict=True)
    if provider.name != 'terraform-provider-aws_v6.74.0_x5.exe' or archive.name != 'terraform-provider-aws_6.74.0_windows_amd64.zip':
        raise ValueError('Exact AWS provider 6.74.0 Windows binary/archive required')
    expected = next(line.split()[0] for line in args.checksums.read_text().splitlines() if line.split()[-1].lstrip('*') == archive.name)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        raise ValueError('Archive checksum mismatch')
    with zipfile.ZipFile(archive) as contents:
        member_hash = hashlib.sha256(contents.read(provider.name)).digest()
    if hashlib.sha256(provider.read_bytes()).digest() != member_hash:
        raise ValueError('Installed provider does not match verified archive')

    result = {'provider_archive_checksum_verified': True, 'installed_binary_matches_archive': True,
              'certificate_verification_required': True, 'cloud_rpc_sent': False}
    temporary_root = pathlib.Path('.tools').resolve()
    temporary_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mtls-diagnostic-', dir=temporary_root) as location:
        directory = pathlib.Path(location)
        key = ec.generate_private_key(ec.SECP521R1())
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')])
        now = datetime.datetime.utcnow()
        certificate = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=1))
            .not_valid_after(now + datetime.timedelta(hours=1))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost')]), critical=False)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH, ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .add_extension(x509.KeyUsage(digital_signature=True, key_encipherment=True, key_agreement=True,
                key_cert_sign=True, content_commitment=False, data_encipherment=False, crl_sign=True,
                encipher_only=False, decipher_only=False), critical=True).sign(key, hashes.SHA256()))
        client_pem = certificate.public_bytes(serialization.Encoding.PEM)
        cert_path, key_path = directory/'client.pem', directory/'client-key.pem'
        cert_path.write_bytes(client_pem)
        key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
        cert_path.chmod(0o600)
        key_path.chmod(0o600)
        # Do not pass cloud credential environment variables into the plugin.
        environment = {k: v for k, v in os.environ.items() if not k.startswith(('AWS_', 'TF_', 'PLUGIN_'))}
        environment.update(TF_PLUGIN_MAGIC_COOKIE='d602bf8f470bc67ca7faa0386276bbdd4330efaf76d1a219cb4d6991ca9872b2',
                           PLUGIN_PROTOCOL_VERSIONS='5', PLUGIN_CLIENT_CERT=client_pem.decode(), AWS_EC2_METADATA_DISABLED='true')
        process = subprocess.Popen([str(provider)], env=environment, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            lines = queue.Queue()
            threading.Thread(target=lambda: lines.put(process.stdout.readline()), daemon=True).start()
            parts = lines.get(timeout=30).decode().strip().split('|')
            if len(parts) < 6 or parts[2] != 'tcp':
                raise ValueError('Unexpected plugin handshake')
            host, port = parts[3].rsplit(':', 1)
            if not ipaddress.ip_address(host).is_loopback:
                raise ValueError('Refusing a non-loopback endpoint')
            der = base64.b64decode(parts[5] + '=' * ((-len(parts[5])) % 4), validate=True)
            pinned = x509.load_der_x509_certificate(der)
            if 'localhost' not in pinned.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName):
                raise ValueError('Advertised certificate does not name localhost')
            result['advertised_certificate_self_issued'] = pinned.subject == pinned.issuer
            pinned.public_key().verify(pinned.signature, pinned.tbs_certificate_bytes, ec.ECDSA(pinned.signature_hash_algorithm))
            result['advertised_certificate_self_signature_valid'] = True
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(der))
            context.load_cert_chain(cert_path, key_path)
            try:
                with socket.create_connection((host, int(port)), timeout=10) as raw:
                    with context.wrap_socket(raw, server_hostname='localhost') as connection:
                        result['verified_hostname_and_pinned_tls'] = hashlib.sha256(connection.getpeercert(binary_form=True)).digest() == hashlib.sha256(der).digest()
            except ssl.SSLCertVerificationError:
                result['verified_hostname_and_pinned_tls'] = False
                result['certificate_validation_failed'] = True

            validation = []
            def verify_callback(connection, offered, error_number, depth, original_ok):
                peer = offered.to_cryptography()
                validation.append({'depth': depth, 'verification_error': error_number,
                    'original_verification_ok': bool(original_ok),
                    'matches_advertised_certificate': peer.fingerprint(hashes.SHA256()) == pinned.fingerprint(hashes.SHA256()),
                    'self_issued': peer.subject == peer.issuer,
                    'issuer_matches_advertised': peer.issuer == pinned.issuer})
                return bool(original_ok)  # Never override a verification failure.
            peer_context = SSL.Context(SSL.TLS_CLIENT_METHOD)
            peer_context.set_min_proto_version(SSL.TLS1_2_VERSION)
            peer_context.get_cert_store().add_cert(crypto.X509.from_cryptography(pinned))
            peer_context.use_certificate_file(str(cert_path))
            peer_context.use_privatekey_file(str(key_path))
            peer_context.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_callback)
            with socket.create_connection((host, int(port)), timeout=10) as raw:
                raw.setblocking(False)
                connection = SSL.Connection(peer_context, raw)
                connection.set_connect_state()
                connection.set_tlsext_host_name(b'localhost')
                deadline = time.monotonic() + 10
                try:
                    while True:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            raise TimeoutError('Local TLS handshake timeout')
                        try:
                            connection.do_handshake()
                            result['independent_verified_tls'] = True
                            break
                        except SSL.WantReadError:
                            select.select([raw], [], [], remaining)
                        except SSL.WantWriteError:
                            select.select([], [raw], [], remaining)
                except SSL.Error:
                    result['independent_verified_tls'] = False
                finally:
                    connection.close()
            result['peer_validation'] = validation
            result['certificate_substitution_observed'] = any(item['depth'] == 0 and not item['matches_advertised_certificate'] for item in validation)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
            process.stdout.close()
    return result


if __name__ == '__main__':
    try:
        outcome = diagnose(arguments())
        print(json.dumps(outcome, indent=2))
        raise SystemExit(0 if outcome.get('verified_hostname_and_pinned_tls') and not outcome.get('certificate_substitution_observed') else 1)
    except Exception as error:
        print(json.dumps({'diagnostic_completed': False, 'error_type': type(error).__name__, 'result': 'NOT PASS'}))
        raise SystemExit(2)
