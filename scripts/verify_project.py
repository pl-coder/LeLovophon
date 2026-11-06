#!/usr/bin/env python3
"""Check packaged design data. This never establishes physical performance."""
import ast
import hashlib
import json
import math
import sys
import zipfile
import xml.etree.ElementTree as ET
from fractions import Fraction
from functools import reduce
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = {'.mov', '.mp4', '.gif', '.png', '.jpg', '.jpeg', '.blend', '.blend1', '.mid', '.wav', '.mp3', '.flac', '.zip'}

def require(ok, message):
    if not ok:
        raise AssertionError(message)

def main():
    manifest = json.loads((ROOT / 'docs/asset-manifest.json').read_text())
    checked = 0
    for item in manifest['files']:
        if item['storage'] != 'git':
            continue
        file = ROOT / item['path']
        require(file.is_file(), f"Missing file: {item['path']}")
        require(hashlib.sha256(file.read_bytes()).hexdigest() == item['sha256'], f"Manifest differs: {item['path']}")
        checked += 1
    actual = [p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts]
    require(not [p for p in actual if p.suffix.lower() in MEDIA], 'Media export included')
    require(not [p for p in actual if p.stat().st_size >= 100 * 1024 * 1024], 'File exceeds ordinary GitHub Git limit')
    for p in actual:
        if p.suffix == '.py':
            ast.parse(p.read_text(), filename=str(p.relative_to(ROOT)))
    audit = json.loads((ROOT / 'outputs/Lovophone_Lab_Frame_Ratio_Audit.json').read_text())
    wanted = list(map(Fraction, ['1','9/8','5/4','3/2','5/3','2','9/4','5/2','3','10/3','4','9/2']))
    require(len(audit['voices']) == 12, 'Expected twelve voices')
    radius = audit['voices'][0]['arm_radius_mm']
    for row, ratio in zip(audit['voices'], wanted):
        require(Fraction(row['pitch_and_rotation_ratio']) == ratio, 'Pitch/rotation ratio differs')
        require(Fraction(row['driver_teeth'], row['driven_teeth']) == ratio, 'Tooth ratio differs')
        require(math.isclose(row['speaking_length_mm'] * float(ratio), 330, abs_tol=1e-8), 'Inverse string length differs')
        require(math.isclose(row['arm_radius_mm'] * float(ratio), radius, abs_tol=1e-8), 'Inverse arm length differs')
    require(reduce(math.lcm, (r.denominator for r in wanted)) * 20 == 480, 'Repeat is not480 s')
    native = ROOT / 'outputs/Lovophone_Lab_Frame_Ratio_Review.FCStd'
    with zipfile.ZipFile(native) as archive:
        require(archive.testzip() is None, 'Native CAD ZIP is damaged')
        tree = ET.fromstring(archive.read('Document.xml'))
    motion = next(x for x in tree.findall('./ObjectData/Object') if x.attrib['name'] == 'Motion')
    prop = motion.find("./Properties/Property[@name='LinkageGeometry']/String")
    rows = json.loads(prop.attrib['value'])
    require(len(rows) == 12, 'Native CAD does not contain twelve voices')
    for row, ratio in zip(rows, wanted):
        require(Fraction(row['driver_teeth'], row['driven_teeth']) == ratio, 'Native drive differs from audit')
        require(Fraction(row['pitch_ratio_exact']) == ratio, 'Native pitch differs')
        require(math.isclose(row['ratio'], float(ratio), abs_tol=1e-12), 'Native animation ratio differs')
    for name in ['Prototype_A_CAD_Check.json', 'Prototype_A_High_Arm_Check.json']:
        result = json.loads((ROOT / 'outputs/Lovophone_Prototype_A' / name).read_text())
        require(not result['invalid_shapes'], f'Invalid recorded CAD shape: {name}')
        require(not result['moving_rigid_to_fixed_intersections'], f'Recorded rigid interference: {name}')
        require(result['physical_test_passed'] is False, 'Do not imply an unperformed physical test passed')
    require(audit['production_released'] is False, 'Known unfinished drive must not be marked released')
    print(f'PASS: {checked} packaged files, source syntax, native CAD ratios, 480-second mathematics and recorded fixture checks. No media included.')
    print('Hardware remains untested; these checks are not manufacturing or physical certification.')

if __name__ == '__main__':
    try:
        main()
    except (AssertionError, ValueError, KeyError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        raise SystemExit(1)
