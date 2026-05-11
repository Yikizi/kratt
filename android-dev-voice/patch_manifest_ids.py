#!/usr/bin/env python3
"""Patch old Termux aapt binary manifest resource IDs for modern Android parser.

The Termux aapt package can emit android:name as framework attr 0x0101056c,
which PackageManager does not treat as android:name. Patch the binary XML
resource map to canonical attr IDs.
"""
from __future__ import annotations

import io
import struct
import sys
import zipfile
from pathlib import Path

ATTR_IDS = {
    "label": 0x01010001,
    "name": 0x01010003,
    "minSdkVersion": 0x0101020C,
    "versionCode": 0x0101021B,
    "versionName": 0x0101021C,
    "targetSdkVersion": 0x01010270,
    "usesCleartextTraffic": 0x010104ec,
}

RES_XML_TYPE = 0x0003
STRING_POOL_TYPE = 0x0001
RESOURCE_MAP_TYPE = 0x0180
UTF8_FLAG = 0x00000100


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def read_len8(data: bytes, off: int) -> tuple[int, int]:
    first = data[off]
    if first & 0x80:
        return ((first & 0x7F) << 8) | data[off + 1], off + 2
    return first, off + 1


def read_len16(data: bytes, off: int) -> tuple[int, int]:
    first = u16(data, off)
    if first & 0x8000:
        return ((first & 0x7FFF) << 16) | u16(data, off + 2), off + 4
    return first, off + 2


def parse_string_pool(data: bytes, off: int) -> tuple[list[str], int]:
    chunk_size = u32(data, off + 4)
    header_size = u16(data, off + 2)
    string_count = u32(data, off + 8)
    flags = u32(data, off + 16)
    strings_start = u32(data, off + 20)
    is_utf8 = bool(flags & UTF8_FLAG)
    offsets = [u32(data, off + header_size + i * 4) for i in range(string_count)]
    strings: list[str] = []
    base = off + strings_start
    for rel in offsets:
        pos = base + rel
        if is_utf8:
            _, pos = read_len8(data, pos)  # utf16 length
            byte_len, pos = read_len8(data, pos)
            strings.append(data[pos : pos + byte_len].decode("utf-8", "replace"))
        else:
            char_len, pos = read_len16(data, pos)
            raw = data[pos : pos + char_len * 2]
            strings.append(raw.decode("utf-16le", "replace"))
    return strings, off + chunk_size


def encode_utf16_string(value: str) -> bytes:
    raw = value.encode("utf-16le")
    length = len(value)
    if length >= 0x8000:
        raise ValueError("string too long")
    return struct.pack("<H", length) + raw + b"\x00\x00"


def build_string_pool(strings: list[str]) -> bytes:
    header_size = 28
    offsets: list[int] = []
    payload = bytearray()
    for value in strings:
        offsets.append(len(payload))
        payload.extend(encode_utf16_string(value))
    while len(payload) % 4:
        payload.append(0)
    strings_start = header_size + len(offsets) * 4
    chunk_size = strings_start + len(payload)
    header = struct.pack(
        "<HHIIIIII",
        STRING_POOL_TYPE,
        header_size,
        chunk_size,
        len(strings),
        0,  # style count
        0,  # flags: UTF-16
        strings_start,
        0,  # styles start
    )
    return header + b"".join(struct.pack("<I", off) for off in offsets) + bytes(payload)


def build_resource_map(strings: list[str]) -> bytes:
    # Resource map entries are indexed by string-pool index. Keep zero for non-framework attrs.
    values = [ATTR_IDS.get(value, 0) for value in strings]
    header_size = 8
    chunk_size = header_size + len(values) * 4
    return struct.pack("<HHI", RESOURCE_MAP_TYPE, header_size, chunk_size) + b"".join(
        struct.pack("<I", value) for value in values
    )


def start_element(line: int, name_idx: int, attrs: list[tuple[int, int, int]]) -> bytes:
    # attrs: (namespace_idx, attr_name_idx, int_value)
    attr_count = len(attrs)
    chunk_size = 36 + attr_count * 20
    out = bytearray()
    out.extend(struct.pack("<HHI", 0x0102, 16, chunk_size))
    out.extend(struct.pack("<II", line, 0xFFFFFFFF))
    out.extend(struct.pack("<II", 0xFFFFFFFF, name_idx))
    out.extend(struct.pack("<HHHHHH", 20, 20, attr_count, 0, 0, 0))
    for ns_idx, attr_name_idx, value in attrs:
        out.extend(struct.pack("<IIIHBBI", ns_idx, attr_name_idx, 0xFFFFFFFF, 8, 0, 0x10, value))
    return bytes(out)


def end_element(line: int, name_idx: int) -> bytes:
    return struct.pack("<HHIIIII", 0x0103, 16, 24, line, 0xFFFFFFFF, 0xFFFFFFFF, name_idx)


def patch_manifest(blob: bytes) -> bytes:
    if u16(blob, 0) != RES_XML_TYPE:
        raise SystemExit("not a binary XML file")

    # Parse top-level chunks.
    chunks: list[tuple[int, bytes]] = []
    pos = 8
    strings: list[str] | None = None
    while pos < len(blob):
        chunk_type = u16(blob, pos)
        chunk_size = u32(blob, pos + 4)
        chunk = blob[pos : pos + chunk_size]
        if chunk_type == STRING_POOL_TYPE and strings is None:
            strings, _ = parse_string_pool(blob, pos)
        chunks.append((chunk_type, chunk))
        pos += chunk_size
    if strings is None:
        raise SystemExit("string pool not found")

    required = ["uses-sdk", "minSdkVersion", "targetSdkVersion", "usesCleartextTraffic"]
    for value in required:
        if value not in strings:
            strings.append(value)
    idx = {value: i for i, value in enumerate(strings)}

    new_chunks: list[bytes] = []
    inserted_uses_sdk = False
    patched_maps = 0
    for chunk_type, chunk in chunks:
        if chunk_type == STRING_POOL_TYPE:
            new_chunks.append(build_string_pool(strings))
            continue
        if chunk_type == RESOURCE_MAP_TYPE:
            new_chunks.append(build_resource_map(strings))
            patched_maps += 1
            continue
        # Add android:usesCleartextTraffic="true" to <application> for localhost bridge.
        if chunk_type == 0x0102:
            name_idx = u32(chunk, 20)
            if name_idx < len(strings) and strings[name_idx] == "application":
                old_count = u16(chunk, 28)
                new_chunk = bytearray(chunk)
                struct.pack_into("<I", new_chunk, 4, len(new_chunk) + 20)
                struct.pack_into("<H", new_chunk, 28, old_count + 1)
                android_ns = idx["http://schemas.android.com/apk/res/android"]
                new_chunk.extend(
                    struct.pack(
                        "<IIIHBBI",
                        android_ns,
                        idx["usesCleartextTraffic"],
                        0xFFFFFFFF,
                        8,
                        0,
                        0x12,  # TYPE_INT_BOOLEAN
                        0xFFFFFFFF,
                    )
                )
                chunk = bytes(new_chunk)

        new_chunks.append(chunk)
        # Insert <uses-sdk android:minSdkVersion="24" android:targetSdkVersion="30" />
        # immediately after the manifest start element.
        if not inserted_uses_sdk and chunk_type == 0x0102:
            name_idx = u32(chunk, 20)
            if name_idx < len(strings) and strings[name_idx] == "manifest":
                android_ns = idx["http://schemas.android.com/apk/res/android"]
                uses_sdk = idx["uses-sdk"]
                new_chunks.append(
                    start_element(
                        2,
                        uses_sdk,
                        [
                            (android_ns, idx["minSdkVersion"], 24),
                            (android_ns, idx["targetSdkVersion"], 30),
                        ],
                    )
                )
                new_chunks.append(end_element(2, uses_sdk))
                inserted_uses_sdk = True

    body = b"".join(new_chunks)
    out = struct.pack("<HHI", RES_XML_TYPE, 8, 8 + len(body)) + body
    print(
        f"patched manifest: resource_maps={patched_maps}, inserted_uses_sdk={inserted_uses_sdk}",
        file=sys.stderr,
    )
    return out


def patch_apk(path: Path) -> None:
    with zipfile.ZipFile(path, "r") as zin:
        entries = [(info, zin.read(info.filename)) for info in zin.infolist()]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for info, payload in entries:
            if info.filename == "AndroidManifest.xml":
                payload = patch_manifest(payload)
            zout.writestr(info, payload)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_manifest_ids.py <apk>")
    patch_apk(Path(sys.argv[1]))
