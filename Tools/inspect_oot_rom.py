"""Read-only measurements of a user-supplied OoT PAL 1.1 ROM.

No ROM bytes, models, textures or extracted files are written. Supply the public
zeldaret PAL 1.1 segments.csv separately; see Documentation/oot-rom-study.md.
Only the matching revision is accepted. This is a format inspector, not an
emulator, and does not reproduce the game's complete runtime rendering.
"""
import argparse
from collections import Counter, defaultdict
import copy
import csv
import hashlib
import json
from pathlib import Path
import struct
import zipfile

EXPECTED_MD5 = 'd714580dd74c2c033f5e1b6dc0aeac77'
DMA_OFFSET = 0x7950
FORMATS = {0: 'RGBA', 1: 'YUV', 2: 'CI', 3: 'IA', 4: 'I'}
BITS = {0: 4, 1: 8, 2: 16, 3: 32}


def load_rom(path):
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            candidates = [item for item in archive.infolist()
                          if Path(item.filename).suffix.lower() == '.z64']
            if len(candidates) != 1 or candidates[0].file_size > 64 * 1024 * 1024:
                raise ValueError('Expected exactly one ROM of at most 64 MiB')
            data = archive.read(candidates[0])
    else:
        if path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('ROM is larger than 64 MiB')
        data = path.read_bytes()
    if data[:4] != bytes.fromhex('80371240'):
        raise ValueError('Expected a big-endian .z64 ROM')
    if hashlib.md5(data).hexdigest() != EXPECTED_MD5:
        raise ValueError('This inspector supports the verified PAL 1.1 revision only')
    return data


def decode_yaz0(data):
    if data[:4] != b'Yaz0':
        raise ValueError('Compressed DMA file has no Yaz0 header')
    size = int.from_bytes(data[4:8], 'big')
    output = bytearray()
    cursor, code, bits = 16, 0, 0
    while len(output) < size:
        if not bits:
            code = data[cursor]
            cursor += 1
            bits = 8
        if code & 0x80:
            output.append(data[cursor])
            cursor += 1
        else:
            first, second = data[cursor:cursor+2]
            cursor += 2
            distance = ((first & 15) << 8) + second + 1
            length = first >> 4
            if not length:
                length = data[cursor] + 0x12
                cursor += 1
            else:
                length += 2
            if distance > len(output) or len(output) + length > size:
                raise ValueError('Invalid Yaz0 back-reference')
            for _ in range(length):
                output.append(output[-distance])
        code = (code << 1) & 255
        bits -= 1
    return bytes(output)


def commands(data):
    """Default scene/room header, excluding alternate headers."""
    for offset in range(0, min(256, len(data)), 8):
        first, second = struct.unpack_from('>II', data, offset)
        yield first >> 24, first, second
        if first >> 24 == 0x14:
            return
    raise ValueError('No scene/room header terminator')


def collision(data):
    pointer = next(second & 0xFFFFFF for code, _, second in commands(data) if code == 3)
    vertex_count = struct.unpack_from('>H', data, pointer + 12)[0]
    vertices = struct.unpack_from('>I', data, pointer + 16)[0] & 0xFFFFFF
    polygon_count = struct.unpack_from('>H', data, pointer + 20)[0]
    polygons = struct.unpack_from('>I', data, pointer + 24)[0] & 0xFFFFFF
    assert vertices + vertex_count * 6 <= len(data)
    assert polygons + polygon_count * 16 <= len(data)
    types = set()
    for index in range(polygon_count):
        kind, a, b, c = struct.unpack_from('>4H', data, polygons + index * 16)
        assert max(a & 0x1FFF, b & 0x1FFF, c & 0x1FFF) < vertex_count
        types.add(kind)
    return {'vertices': vertex_count, 'polygons': polygon_count,
            'surface_types': len(types), 'bounds_native_units':
            struct.unpack_from('>6h', data, pointer)}


def inspect_room(files, name):
    scene, room = files[name + '_scene'], files[name + '_room_0']
    segments = {2: scene, 3: room}
    unknown, draws = [], []
    cache, loaded, tiles, texture_sizes, opcodes = {}, {}, {}, Counter(), Counter()
    state = {'texture': None, 'geometry': 0}

    def read(pointer, size):
        segment, offset = pointer >> 24, pointer & 0xFFFFFF
        data = segments.get(segment)
        if data is None or offset + size > len(data):
            raise ValueError(hex(pointer))
        return data[offset:offset+size]

    mesh = next(second for code, _, second in commands(room) if code == 0x0A)
    kind, count = read(mesh, 2)
    assert kind == 2, 'Selected room must use RoomShapeCullable'
    entries = int.from_bytes(read(mesh + 4, 4), 'big')
    roots = []
    for index in range(count):
        roots.extend(pointer for pointer in struct.unpack('>II', read(entries + index * 16 + 8, 8)) if pointer)

    def triangle(a, b, c, address):
        indices = [a // 2, b // 2, c // 2]
        if not all(index in cache for index in indices):
            unknown.append({'kind': 'missing_vertex', 'address': hex(address)})
            return
        draws.append({'vertices': [cache[index] for index in indices],
                      'texture': state['texture'], 'address': address})

    def walk(pointer, ancestors=()):
        if pointer in ancestors:
            raise ValueError('Display-list recursion cycle')
        for index in range(10000):
            address = pointer + index * 8
            try:
                first, second = struct.unpack('>II', read(address, 8))
            except ValueError:
                unknown.append({'kind': 'external_display_list', 'address': hex(address)})
                return
            opcode = first >> 24
            opcodes[opcode] += 1
            if opcode == 0xDF:
                return
            if opcode == 0xDE:
                walk(second, ancestors + (pointer,))
                if first & 0x10000:
                    return
            elif opcode == 1:
                number = (first >> 12) & 255
                start = ((first >> 1) & 127) - number
                for vertex in range(number):
                    value = struct.unpack('>hhhHhhBBBB', read(second + vertex * 16, 16))
                    item = {'position': value[:3], 'uv': value[4:6], 'rgba': value[6:],
                            'lit': bool(state['geometry'] & 0x20000)}
                    cache[start + vertex] = item
                    loaded[second + vertex * 16] = item
            elif opcode == 5:
                triangle((first >> 16) & 255, (first >> 8) & 255, first & 255, address)
            elif opcode == 6:
                triangle((first >> 16) & 255, (first >> 8) & 255, first & 255, address)
                triangle((second >> 16) & 255, (second >> 8) & 255, second & 255, address)
            elif opcode == 0xD9:
                state['geometry'] = (state['geometry'] & (first & 0xFFFFFF)) | second
            elif opcode == 0xFD:
                state['texture'] = hex(second)
            elif opcode == 0xF5:
                tiles[(second >> 24) & 7] = ((first >> 21) & 7, (first >> 19) & 3)
            elif opcode == 0xF2:
                left, top = (first >> 12) & 4095, first & 4095
                right, bottom = (second >> 12) & 4095, second & 4095
                tile = (second >> 24) & 7
                fmt, size = tiles[tile]
                texture_sizes[(state['texture'], FORMATS[fmt] + str(BITS[size]),
                               (right-left)//4+1, (bottom-top)//4+1)] += 1
            elif opcode == 0xE1:
                state['branch_target'] = second
            elif opcode == 4:
                # Inspect both conditional branches; this is a static union,
                # not a claim that both branches render together in one frame.
                saved_state, saved_cache, saved_tiles = copy.deepcopy(state), dict(cache), dict(tiles)
                walk(state['branch_target'], ancestors + (pointer,))
                state.clear(); state.update(saved_state)
                cache.clear(); cache.update(saved_cache)
                tiles.clear(); tiles.update(saved_tiles)
            elif opcode == 0xDA:
                unknown.append({'kind': 'unresolved_matrix', 'address': hex(address)})
        raise ValueError('Display list exceeds bounded instruction count')

    for root in roots:
        walk(root)
    edges, uses, exact = defaultdict(set), Counter(), Counter()
    unlit_colors = set()
    lit_triangles = 0
    for draw in draws:
        points = [tuple(vertex['position']) for vertex in draw['vertices']]
        if all(vertex['lit'] for vertex in draw['vertices']):
            lit_triangles += 1
        unlit_colors.update(vertex['rgba'] for vertex in draw['vertices'] if not vertex['lit'])
        exact[tuple(sorted(points))] += 1
        for a, b in zip(points, points[1:] + points[:1]):
            edge = tuple(sorted((a, b)))
            edges[edge].add(draw['texture'])
            uses[edge] += 1
    return {'scene': name, 'scope': 'default scene header and room 0; both conditional detail branches',
            'scene_bytes': len(scene), 'room0_bytes': len(room), 'culling_groups': count,
            'display_list_roots': len(roots), 'static_triangle_instances': len(draws),
            'distinct_loaded_vertex_records': len(loaded),
            'texture_image_references': len({draw['texture'] for draw in draws}),
            'lit_triangle_instances': lit_triangles, 'unlit_vertex_colors': len(unlit_colors),
            'render_tiles': [{'image_pointer': image, 'format': fmt, 'width': width,
                              'height': height, 'settings': frequency}
                             for (image, fmt, width, height), frequency in texture_sizes.items()],
            'material_shared_geometric_edges': sum(len(values) > 1 for values in edges.values()),
            'render_boundary_edges': sum(number == 1 for number in uses.values()),
            'duplicate_geometric_triangle_instances': sum(number-1 for number in exact.values() if number > 1),
            'collision': collision(scene), 'unresolved_commands': unknown}


def inspect(rom, segments_path):
    with segments_path.open() as stream:
        names = [row['Name'] for row in csv.DictReader(stream)]
    entries, files, addresses = [], {}, {}
    for index, name in enumerate(names):
        start, end, physical, compressed_end = struct.unpack_from('>4I', rom, DMA_OFFSET + index * 16)
        assert 0 <= start < end and physical != 0xFFFFFFFF
        data = rom[physical:compressed_end] if compressed_end else rom[physical:physical+end-start]
        if compressed_end:
            data = decode_yaz0(data)
        assert len(data) == end-start, name
        entries.append({'name': name, 'virtual_start': start, 'size': end-start,
                        'compressed': bool(compressed_end)})
        addresses[start] = name
        files[name] = data
    assert struct.unpack_from('>4I', rom, DMA_OFFSET + len(entries) * 16) == (0, 0, 0, 0)
    scenes = []
    for name, data in files.items():
        if not name.endswith('_scene'):
            continue
        room_files = []
        for code, first, second in commands(data):
            if code == 4:
                for index in range((first >> 16) & 255):
                    virtual = struct.unpack_from('>I', data, (second & 0xFFFFFF) + index * 8)[0]
                    room_files.append(addresses[virtual])
        scenes.append({'name': name, 'room_files': room_files, 'collision': collision(data)})
    return {'rom': {'bytes': len(rom), 'sha256': hashlib.sha256(rom).hexdigest(),
                    'md5': hashlib.md5(rom).hexdigest(), 'title': rom[0x20:0x34].decode().strip(),
                    'region': chr(rom[0x3E]), 'revision': rom[0x3F]},
            'inventory': {'dma_files': len(entries), 'yaz0_files': sum(item['compressed'] for item in entries),
                          'decompressed_file_bytes': sum(item['size'] for item in entries),
                          'object_files': sum(name.startswith('object_') for name in files),
                          'overlay_files': sum(name.startswith('ovl_') for name in files),
                          'scene_files': len(scenes), 'room_files': sum('_room_' in name for name in files),
                          'validated_scene_collision_polygons': sum(scene['collision']['polygons'] for scene in scenes)},
            'selected_rooms': [inspect_room(files, name) for name in ('spot01', 'spot00', 'spot04')],
            'scenes': scenes,
            'limitations': ['Not an emulator or per-frame renderer.',
                            'Scene/room measurements use default headers only; alternate layouts and dynamic actors are excluded.',
                            'Unresolved external display lists are reported, not guessed.',
                            'No extracted game assets are written.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--segments', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inspect(load_rom(args.rom), args.segments)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['inventory'], indent=2))


if __name__ == '__main__':
    main()
