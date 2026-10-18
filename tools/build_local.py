"""Translate your own verified FIFA Street 2 XBE into private C and build the native PC port.

Everything produced (runtime download, disassembly, generated C, build) stays in --local-dir
(default .local/), which is excluded from version control. Never upload it.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
KIT = json.loads((ROOT / 'kit.json').read_text(encoding='utf-8'))
sys.path.insert(0, str(ROOT / 'tools'))
import validate_game  # noqa: E402

RUNTIME = KIT['runtime']
# Functions whose entries the disassembler rejects (an overlapping decode already starts
# there); their boundaries are known from the original code, so they are listed directly.
MANUAL_FUNCTIONS = [
    {'start': '0x000FA9A0', 'end': '0x000FABD5'},   # player creator, mov [ecx+0x238], 0xFA9A0
    {'start': '0x00213C19', 'end': '0x00213C5A'},   # mov [edx], 0x213C19
    {'start': '0x0016F2C0', 'end': '0x0016F3BE'},   # front-end update, hidden by a false gap prologue at 0x16F29E
]
# Functions the disassembler cuts short (seeds land on its case labels); the true end is given so
# every branch and the jump table at the end stay inside one translated function.
FUNCTION_ENDS = {
    0x00227853: 0x002279A1,   # command worker: 31-entry jump table at 0x2279A1
}


def run(args, cwd, env):
    print('Running:', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), cwd=cwd, env=env, check=True)


def prepare_runtime(local):
    """xboxrecomp runtime + translator (with the Street 1 port's fixes) from the pinned public fifa-street-pc commit."""
    target = local / 'runtime'
    if (target / 'xboxrecomp/CMakeLists.txt').is_file():
        return target
    archive = local / 'downloads' / f'fifa-street-pc-{RUNTIME["commit"]}.tar.gz'
    if not archive.is_file():
        print('Downloading', RUNTIME['url'], flush=True)
        archive.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(RUNTIME['url']) as response:
            archive.write_bytes(response.read())
    with tarfile.open(archive) as bundle:
        for member in bundle.getmembers():
            parts = Path(member.name).parts
            if len(parts) < 2 or not member.isfile():
                continue
            relative = Path(*parts[1:])
            if relative.parts[0] != 'xboxrecomp' and relative.as_posix() != 'street1/translate-ebp-boundaries.py':
                continue
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(bundle.extractfile(member).read())
    return target


def generate(xbe, local, runtime, env):
    source = local / 'source/street2'
    if source.exists():
        shutil.rmtree(source)
    shutil.copytree(ROOT / 'street2', source)
    gen = source / 'project/src/recomp/gen'
    work = local / 'recomp-work'
    if work.exists():
        shutil.rmtree(work)
    disasm, ident, abi = work / 'disasm', work / 'ident', work / 'abi'
    for directory in (disasm, ident, abi, gen):
        directory.mkdir(parents=True, exist_ok=True)
    py, tools = sys.executable, runtime / 'xboxrecomp'
    seeds = []
    for name in ('seed_functions.json', 'seed_manual.json'):
        seeds += ['--seed-functions', source / 'hle' / name]
    run([py, '-m', 'tools.disasm', xbe, '--text-only', '--extra-sections', 'D3D,XGRPH,DSOUND,XPP,DOLBY',
         '--force', *seeds, '--output', disasm], tools, env)
    functions_path = disasm / 'functions.json'
    functions = json.loads(functions_path.read_text(encoding='utf-8'))
    known = {int(f['start'], 16) for f in functions}
    for entry in functions:
        end = FUNCTION_ENDS.get(int(entry['start'], 16))
        if end:
            entry['end'], entry['size'] = f'0x{end:08X}', end - int(entry['start'], 16)
    for manual in MANUAL_FUNCTIONS:
        start, end = int(manual['start'], 16), int(manual['end'], 16)
        if start not in known:
            functions.append({'start': manual['start'], 'end': manual['end'], 'size': end - start,
                              'name': f'sub_{start:08X}', 'section': '.text', 'confidence': 0.95,
                              'detection_method': 'seed_manual', 'num_instructions': 0, 'has_prologue': False,
                              'calls_to': [], 'called_by': []})
    functions.sort(key=lambda f: int(f['start'], 16))
    functions_path.write_text(json.dumps(functions, indent=2), encoding='utf-8')
    run([py, '-m', 'tools.func_id', xbe, '--functions', functions_path, '--strings', disasm / 'strings.json',
         '--xrefs', disasm / 'xrefs.json', '--output', ident], tools, env)
    run([py, '-m', 'tools.abi_analysis', xbe, '--disasm-dir', disasm, '--func-id-dir', ident,
         '--output', abi / 'abi_functions.json'], tools, env)
    run([py, '-m', 'tools.recomp', xbe, '--game-name', 'FIFA Street 2', '--all', '--split', '250',
         '--disasm-dir', disasm, '--func-id-dir', ident, '--abi-dir', abi, '--gen-dir', gen], tools, env)
    missing = [m['start'] for m in MANUAL_FUNCTIONS
               if not any(f'void sub_{int(m["start"], 16):08X}(void)' in p.read_text(encoding='utf-8', errors='replace')
                          for p in gen.glob('recomp_*.c'))]
    if missing:
        raise ValueError('Translation is missing required functions: ' + ', '.join(missing))
    # Post-passes, in the order the port was validated with.
    run([py, source / 'hle/translate-nv-interrupt-writes.py'], source, env)
    run([py, runtime / 'street1/translate-ebp-boundaries.py', '--apply', '--directory', gen], source, env)
    run([py, source / 'hle/make-smp-serial.py'], source, env)
    run([py, source / 'hle/apply-hle-wrappers.py'], source, env)
    (local / 'generation-complete.json').write_text(json.dumps({'xbeSha256': KIT['required_files']['default.xbe']}) + '\n',
                                                    encoding='utf-8')
    return source / 'project'


def developer_environment():
    """MSVC headers/libraries for clang-cl (from the Visual Studio vcvars64 script)."""
    if os.name != 'nt' or os.environ.get('VCToolsInstallDir'):
        return {key.upper() if os.name == 'nt' else key: value for key, value in os.environ.items()}
    vswhere = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Microsoft Visual Studio/Installer/vswhere.exe'
    if not vswhere.is_file():
        raise ValueError('Visual Studio 2022 (Build Tools) with the C++ workload is required')
    install = subprocess.check_output([str(vswhere), '-latest', '-products', '*', '-requires',
                                       'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                                       '-property', 'installationPath'], text=True).strip()
    vcvars = Path(install) / 'VC/Auxiliary/Build/vcvars64.bat'
    output = subprocess.check_output(f'"{vcvars}" >nul && set', shell=True, text=True)
    return {key.upper(): value for key, value in (line.split('=', 1) for line in output.splitlines() if '=' in line)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-files', type=Path, required=True, help='Extracted disc folder named game_files')
    parser.add_argument('--local-dir', type=Path, default=ROOT / '.local')
    parser.add_argument('--llvm-dir', type=Path, help='LLVM install folder containing bin/clang-cl (default: PATH)')
    parser.add_argument('--reuse-generated', action='store_true', help='Skip the translation after a completed one')
    parser.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 4) - 2))
    args = parser.parse_args()
    game_files = args.game_files.resolve()
    problems = validate_game.validate(game_files)
    if problems:
        raise ValueError('Unsupported game files: ' + '; '.join(problems))
    if os.name != 'nt':
        raise ValueError('This kit currently builds on Windows only')
    local = args.local_dir.resolve()
    local.mkdir(parents=True, exist_ok=True)
    env = developer_environment()
    if args.llvm_dir:
        env['PATH'] = str(args.llvm_dir.resolve() / 'bin') + os.pathsep + env.get('PATH', '')
    clang_cl, cmake, ninja = (shutil.which(n, path=env.get('PATH')) for n in ('clang-cl', 'cmake', 'ninja'))
    if not (clang_cl and cmake and ninja):
        raise ValueError('clang-cl, cmake and ninja must be on PATH (or pass --llvm-dir)')
    runtime = prepare_runtime(local)
    stamp = local / 'generation-complete.json'
    if args.reuse_generated and stamp.is_file():
        project = local / 'source/street2/project'
    else:
        stamp.unlink(missing_ok=True)
        project = generate(game_files / 'default.xbe', local, runtime, env)
    build = local / 'build'
    run([cmake, '-S', project, '-B', build, '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=RelWithDebInfo',
         '-DCMAKE_C_COMPILER=' + clang_cl, '-DXBOXRECOMP_DIR=' + str(runtime / 'xboxrecomp')], local, env)
    run([cmake, '--build', build, '--parallel', str(args.jobs), '--target', 'fifastreet_recomp'], local, env)
    print('Built privately in', build)
    print('Play with: python tools/play.py --game-files', game_files)
    print('Do not upload .local/, the generated code or the executable.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('Build failed:', error, file=sys.stderr)
        sys.exit(1)
