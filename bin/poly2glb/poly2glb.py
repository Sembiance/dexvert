#!/usr/bin/env python3
# Vibe coded by Claude
"""
poly2glb - Convert 3D model files to GLB (glTF Binary) format.

Usage: poly2glb <type> <inputFile> <outputFile.glb>

Supported types:
  sketchUp  - SketchUp .skp files
"""

import sys
import os

# Add script directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)


def convert_sketchup(input_path, output_path, verbose=False):
    """Convert a SketchUp file to GLB."""
    from sketchUp import parse_skp, convert_to_glb

    print(f"Parsing SketchUp file: {input_path}")
    model = parse_skp(input_path, verbose=verbose)

    print(f"  Version: {model.version_string}")
    print(f"  Vertices: {len(model.vertices)}")
    print(f"  Edges: {len(model.edges)}")
    print(f"  Faces: {len(model.faces)}")
    print(f"  Materials: {len(model.materials)}")
    print(f"  Layers: {len(model.layers)}")

    faces_with_verts = sum(1 for f in model.faces if f.vertices and len(f.vertices) >= 3)
    print(f"  Faces with geometry: {faces_with_verts}")

    print(f"Converting to GLB: {output_path}")
    convert_to_glb(model, output_path, verbose=verbose)
    print(f"Done. Output: {output_path}")


def convert_electricimage3d(input_path, output_path, verbose=False):
    """Convert an Electric Image 3D file to GLB."""
    from electricImage3D import parse_ei3d, convert_to_glb

    print(f"Parsing Electric Image 3D file: {input_path}")
    model = parse_ei3d(input_path, verbose=verbose)

    total_verts = sum(len(g.vertices) for g in model.groups)
    total_faces = sum(len(g.faces) for g in model.groups)
    print(f"  Groups: {len(model.groups)}")
    print(f"  Vertices: {total_verts}")
    print(f"  Faces: {total_faces}")

    print(f"Converting to GLB: {output_path}")
    convert_to_glb(model, output_path, verbose=verbose)
    print(f"Done. Output: {output_path}")


# Converter registry - add new types here
CONVERTERS = {
    'sketchUp': convert_sketchup,
    'electricImage3D': convert_electricimage3d,
}


def main():
    if len(sys.argv) < 4:
        print(__doc__, file=sys.stderr)
        print(f"Available types: {', '.join(CONVERTERS.keys())}", file=sys.stderr)
        sys.exit(1)

    conv_type = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    if conv_type not in CONVERTERS:
        print(f"Error: Unknown type '{conv_type}'", file=sys.stderr)
        print(f"Available types: {', '.join(CONVERTERS.keys())}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Create output directory if needed
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    try:
        CONVERTERS[conv_type](input_path, output_path, verbose=verbose)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
