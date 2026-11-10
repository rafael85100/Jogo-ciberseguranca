#!/usr/bin/env python3
"""Assinatura APK v2 (RSA/SHA-256) e verificacao, usando o openssl da maquina."""
import hashlib, struct, subprocess, sys, tempfile, os

V2_ID = 0x7109871a
MAGIC = b'APK Sig Block 42'
ALGO_RSA_PKCS1_SHA256 = 0x0103


def lp(b):
    return struct.pack('<I', len(b)) + b


def split_apk(data):
    eocd = data.rfind(b'PK\x05\x06')
    cd_off, = struct.unpack_from('<I', data, eocd + 16)
    cd_size, = struct.unpack_from('<I', data, eocd + 12)
    assert cd_off + cd_size == eocd, 'zip com comentario/zip64 nao suportado'
    block_start = cd_off
    if data[cd_off - 16:cd_off] == MAGIC:
        sz, = struct.unpack_from('<Q', data, cd_off - 24)
        block_start = cd_off - sz - 8
    return block_start, cd_off, eocd


def content_digest(data, block_start, cd_off, eocd):
    eocd_bytes = bytearray(data[eocd:])
    struct.pack_into('<I', eocd_bytes, 16, block_start)
    chunks = []
    for sec in (data[:block_start], data[cd_off:eocd], bytes(eocd_bytes)):
        for i in range(0, len(sec), 1 << 20):
            c = sec[i:i + (1 << 20)]
            chunks.append(hashlib.sha256(b'\xa5' + struct.pack('<I', len(c)) + c).digest())
    return hashlib.sha256(b'\x5a' + struct.pack('<I', len(chunks)) + b''.join(chunks)).digest()


def openssl(args, inp=None):
    return subprocess.run(['openssl'] + args, input=inp, capture_output=True, check=True).stdout


def sign(unsigned_path, out_path, key_pem, cert_der):
    data = open(unsigned_path, 'rb').read()
    block_start, cd_off, eocd = split_apk(data)
    assert block_start == cd_off, 'APK ja assinado; passe um zip sem bloco de assinatura'
    digest = content_digest(data, cd_off, cd_off, eocd)
    cert = open(cert_der, 'rb').read()
    pub = openssl(['pkey', '-in', key_pem, '-pubout', '-outform', 'DER'])
    digests = lp(lp(struct.pack('<I', ALGO_RSA_PKCS1_SHA256) + lp(digest)))
    signed_data = digests + lp(lp(cert)) + lp(b'')
    sig = openssl(['dgst', '-sha256', '-sign', key_pem], signed_data)
    signer = lp(signed_data) + lp(lp(struct.pack('<I', ALGO_RSA_PKCS1_SHA256) + lp(sig))) + lp(pub)
    value = lp(lp(signer))
    pair = struct.pack('<Q', 4 + len(value)) + struct.pack('<I', V2_ID) + value
    size = len(pair) + 8 + 16
    block = struct.pack('<Q', size) + pair + struct.pack('<Q', size) + MAGIC
    eocd_bytes = bytearray(data[eocd:])
    struct.pack_into('<I', eocd_bytes, 16, cd_off + len(block))
    open(out_path, 'wb').write(data[:cd_off] + block + data[cd_off:eocd] + bytes(eocd_bytes))


def _seq(b):
    out, p = [], 0
    while p < len(b):
        n, = struct.unpack_from('<I', b, p); out.append(b[p + 4:p + 4 + n]); p += 4 + n
    return out


def verify(path):
    data = open(path, 'rb').read()
    block_start, cd_off, eocd = split_apk(data)
    assert block_start != cd_off, 'sem bloco de assinatura'
    p = block_start + 8; end = cd_off - 24
    v2 = None
    while p < end:
        ln, pid = struct.unpack_from('<QI', data, p)
        if pid == V2_ID: v2 = data[p + 12:p + 8 + ln]
        p += 8 + ln
    assert v2 is not None, 'sem assinatura v2'
    expect = content_digest(data, block_start, cd_off, eocd)
    for signer in _seq(_seq(v2)[0]):
        sd, sigs, pub = _seq(signer)
        digests = _seq(_seq(sd)[0]); certs = _seq(_seq(sd)[1])
        for dg in digests:
            algo, = struct.unpack_from('<I', dg); d = _seq(dg[4:])[0]
            if algo in (0x0103, 0x0201, 0x0301):
                assert d == expect, 'digest do conteudo NAO confere (algo %#x)' % algo
        for s in _seq(sigs):
            algo, = struct.unpack_from('<I', s); sv = _seq(s[4:])[0]
            with tempfile.TemporaryDirectory() as td:
                open(td + '/pub.der', 'wb').write(pub); open(td + '/sig', 'wb').write(sv); open(td + '/data', 'wb').write(sd)
                h = {0x0103: '-sha256', 0x0201: '-sha256', 0x0301: '-sha256', 0x0104: '-sha512'}[algo]
                r = subprocess.run(['openssl', 'dgst', h, '-verify', td + '/pub.der', '-keyform', 'DER', '-signature', td + '/sig', td + '/data'], capture_output=True)
                assert r.returncode == 0, 'assinatura invalida: ' + r.stdout.decode() + r.stderr.decode()
        subj = subprocess.run(['openssl', 'x509', '-inform', 'DER', '-noout', '-subject'], input=certs[0], capture_output=True).stdout.decode().strip()
        print('OK v2:', subj, '| algos', [hex(struct.unpack_from('<I', x)[0]) for x in _seq(sigs)])


if __name__ == '__main__':
    if sys.argv[1] == 'verify': verify(sys.argv[2])
    elif sys.argv[1] == 'sign': sign(*sys.argv[2:6])
