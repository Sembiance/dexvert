meta:
  id: ps2ico
  file-extension: ico
  title: PlayStation 2 icon file
  endian: le
types:
  vertex_coord:
    seq:
      - id: x
        type: s2
      - id: y
        type: s2
      - id: z
        type: s2
      - id: unknown
        type: s2
  tex_coord:
    seq:
      - id: u
        type: s2
      - id: v
        type: s2
  vertex_color:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1
      - id: a
        type: u1
  vertex_info:
    seq:
      - id: positions
        type: vertex_coord
        repeat: expr
        repeat-expr: _parent.animation_shapes
      - id: normal
        type: vertex_coord
      - id: tex_coord
        type: tex_coord
      - id: color
        type: vertex_color
  frame_key:
    seq:
      - id: time
        type: f4
      - id: value
        type: f4
  frame_info:
    seq:
      - id: shape_id
        type: u4
      - id: key_count
        type: u4
      - id: keys
        type: frame_key
        repeat: expr
        repeat-expr: key_count
  compressed_texture:
    seq:
      - id: size
        type: u4
      - id: data
        type: u2
        repeat: expr
        repeat-expr: size / 2
  uncompressed_texture:
    seq:
      - id: data
        type: u2
        repeat: expr
        repeat-expr: 128 * 128
seq:
  - id: file_id
    contents: [0x00, 0x00, 0x01, 0x00]

  - id: animation_shapes
    type: u4

  - id: texture_type
    type: u4

  - id: reserved
    type: u4

  - id: vertex_count
    type: u4

  - id: vertices
    type: vertex_info
    repeat: expr
    repeat-expr: vertex_count

  - id: tag_id
    type: u4

  - id: frame_length
    type: u4

  - id: animation_speed
    type: f4

  - id: play_offset
    type: u4

  - id: frame_count
    type: u4

  - id: frames
    type: frame_info
    repeat: expr
    repeat-expr: frame_count
    
  - id: texture
    type: 
      switch-on: texture_type
      cases:
        0x0F: compressed_texture
        _: uncompressed_texture
  
