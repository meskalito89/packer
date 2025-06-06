import os
import sys
import json
import pathspec

MARKER = "--- FILE: {} ---"

def load_ignore_spec(root_dir):
    ignore_file = os.path.join(root_dir, '.packignore')
    if not os.path.exists(ignore_file):
        return None
    with open(ignore_file, 'r', encoding='utf-8') as f:
        patterns = f.read().splitlines()
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)

def is_ignored(path, ignore_spec):
    if ignore_spec is None:
        return False
    return ignore_spec.match_file(path)

def is_text_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except:
        return False

def pack(root_dir, output_format='text'):
    files_data = []

    # Загружаем .packignore из текущей директории
    ignore_spec = load_ignore_spec(root_dir)

    for root, dirs, files in os.walk(root_dir):
        rel_dir = os.path.relpath(root, root_dir)
        if rel_dir == ".":
            rel_dir = ""

        dirs[:] = [d for d in dirs if not is_ignored(os.path.normpath(os.path.join(rel_dir, d)), ignore_spec)]

        for file in files:
            rel_path = os.path.normpath(os.path.join(rel_dir, file))

            if is_ignored(rel_path, ignore_spec):
                continue

            full_path = os.path.join(root_dir, rel_path)

            if not is_text_file(full_path):
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"[error reading] {rel_path}: {e}", file=sys.stderr)
                continue

            if output_format == 'json':
                files_data.append({"path": rel_path, "content": content})
            else:
                print(MARKER.format(rel_path))
                print(content.rstrip())
                print()
            print(f"[packed] {rel_path}", file=sys.stderr)

            print(f"[packed] {rel_path}", file=sys.stderr)

    if output_format == 'json':
        print(json.dumps(files_data, indent=2, ensure_ascii=False))




def unpack(input_file, output_dir):
    with open(input_file, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        f.seek(0)

        if first_line.strip().startswith('['):  # JSON format
            data = json.load(f)
            for item in data:
                write_file(item['path'], item['content'], output_dir)
        else:
            lines = f.readlines()
            unpack_text_format(lines, output_dir)

def unpack_text_format(lines, output_dir):
    current_path = None
    buffer = []

    for line in lines:
        if line.startswith('--- FILE: ') and line.strip().endswith(' ---'):
            if current_path:
                write_file(current_path, ''.join(buffer), output_dir)
            current_path = line[len('--- FILE: '):-5].strip()
            buffer = []
        else:
            buffer.append(line)
    if current_path:
        write_file(current_path, ''.join(buffer), output_dir)

def write_file(rel_path, content, output_dir):
    full_path = os.path.join(output_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[unpacked] {rel_path}")

def usage():
    print("Usage:")
    print("  python packer.py pack <project_dir> [-o json|text] > output.txt")
    print("  python packer.py unpack <input_file> <output_dir>")

if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'pack':
        out_format = 'text'
        if '-o' in sys.argv:
            o_index = sys.argv.index('-o')
            if len(sys.argv) > o_index + 1:
                out_format = sys.argv[o_index + 1]
        pack(sys.argv[2], output_format=out_format)

    elif mode == 'unpack' and len(sys.argv) >= 4:
        unpack(sys.argv[2], sys.argv[3])

    else:
        usage()
