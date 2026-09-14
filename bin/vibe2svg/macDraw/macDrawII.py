# Vibe coded by Codex
"""Independent MacDraw II data-fork decoder and SVG drawing adapter.

The field map is cross-checked against the input structures and public format
research. No LibreOffice/libmwaw code is executed or imported. See macDraw.txt
for the declared rendering profiles and unresolved application metadata.
"""
from __future__ import annotations

import math
import struct
import sys
from bisect import bisect_right
import macDrawText as mt

# Fixed application palette data (one-based indices), not parser code.
COLORS = ('#ffffff','#000000','#dd0806','#008011','#0000d4','#fcf305','#02abeb','#f20885')
PATTERNS = '''
f0f03c3c0f0fc3c3 1111444411114444 7777bbbb7777bbbb 9999cccc9999cccc
0000000000000000 ffffffffffffffff 7f7ffffff7f7ffff 7f7ff7f77f7ff7f7
7777dddd7777dddd 7777777777777777 aaaaaaaaaaaaaaaa 8888888888888888
8888222288882222 8080080880800808 8080000008080000 8080414108081414
ffff8080ffff0808 8181242481812424 8080202008080202 e0e038380e0e8383
7777dddd7777dddd 8888222288882222 9999666699996666 2020808008080202
ffffffffffffffff ffff0000ffff0000 cccc000033330000 f0f0f0f00f0f0f0f
ffff8888ffff8888 aaaaaaaaaaaaaaaa 0101040410104040 83830e0e3838e0e0
eeeebbbbeeeebbbb 1111444411114444 3333cccc3333cccc 4040000004040000
aaaaaaaaaaaaaaaa 8888888888888888 0101101001011010 0000141455551414
ffff808080808080 8282282828288282 8080000000000000 8080020201014040
aaaaaaaaaaaaaaaa 5555555555555555 dddd7777dddd7777 aaaa808088888080
0808222280800202 b1b10303d8d80c0c 888822228888aaaa 8282393982820101
030348480c0c0101 5555404055550404 10105454ffff0404 2020888888880505
bfbfbfbfb0b0b0b0 f8f822228f8f2222 77778f8f7777f8f8
'''.split()
STYLE_SIZES = (24,12,28,14,18)
ZONE_NAMES = ('rulers','pens','dashes','arrows','fonts','layers','layer_names',
              'layer_libraries','libraries','library_names','geometry_heap','text_heap','free_storage')


class Decoder:
    def __init__(self, api, data, fonts, recover, require_complete):
        self.api, self.data = api, data
        self.fonts = fonts or mt.default_fonts()
        self.recover, self.require_complete = recover, require_complete
        self.issues, self.spans = [], []
        self.header = {'native_format':'MacDraw II', 'ruler_units':1}
        self.used_blocks = set()

    def fail(self, message):
        raise self.api.FormatError(message)

    def unpack(self, fmt, offset, end=None):
        n = struct.calcsize('>'+fmt)
        if offset < 0 or offset+n > (len(self.data) if end is None else min(end,len(self.data))):
            self.fail(f'0x{offset:x}: truncated MacDraw II {fmt} field')
        return struct.unpack_from('>'+fmt,self.data,offset)

    def fixed_box(self, offset, end=None):
        return tuple(v/65536 for v in self.unpack('4i',offset,end))

    def problem(self, offset, length, code, detail, damage=False):
        if self.require_complete or (damage and not self.recover):
            self.fail(f'0x{offset:x}: {detail}')
        self.issues.append(self.api.Issue(offset,length,('recovery_' if damage else '')+'macdraw2_'+code,detail))

    def span(self, offset, length, name):
        if length:
            self.spans.append((offset,length,'macdraw2_'+name))

    def pool(self, zone):
        start, length = zone
        if not length:return {}
        limit = start+length
        table_size, free = self.unpack('2I',start,limit)
        if table_size < 8 or table_size%4 or table_size+4 > length:
            self.fail(f'0x{start:x}: invalid MacDraw II handle-table extent')
        base = start+table_size
        data_size, = self.unpack('I',base,limit)
        if data_size < 4 or base+data_size > limit:
            self.fail(f'0x{base:x}: invalid MacDraw II heap extent')
        out={}
        for slot in range((table_size-8)//4):
            relative, = self.unpack('I',start+8+slot*4)
            if not relative:continue
            address = base+relative
            try:
                if relative < 4: self.fail('heap handle points inside its header')
                uses, size = self.unpack('2I',address,base+data_size)
                if size < 8 or address+size > base+data_size:
                    self.fail('heap block exceeds declared heap extent')
                out[slot]=(address,address+size)
            except self.api.FormatError as error:
                self.problem(start+8+slot*4,4,'heap_handle',str(error),True)
        # An allocation may be shared by several handles; distinct blocks must
        # not overlap. Zero/unreferenced slots and allocation gaps are retained.
        previous=base+4
        for a,b in sorted(set(out.values())):
            if a < previous:self.fail(f'0x{a:x}: overlapping MacDraw II heap blocks')
            previous=b
        return out

    def parse(self):
        raw=self.data
        if len(raw)<0x1f4:self.fail('truncated MacDraw II header')
        signature=raw[:8]
        if signature[:4] not in (b'DRWG',b'STAT') or signature[4:] not in (b'D2\x00\x00',b'D2\x00\x01',b'D2\xff\xff',b'\x00'*4):
            self.fail('unsupported MacDraw II signature/subversion')
        subversion=self.unpack('h',6)[0]
        self.header.update(subversion=subversion,stationery=signature[:4]==b'STAT')
        self.span(0,8,'signature');self.span(8,120,'printing_record')
        self.span(128,128,'editor_preferences')
        self.span(256,160,'counts_and_saved_rectangles')
        self.span(416,40,'style_zone_sizes_and_reserved_words')
        self.span(456,44,'storage_zone_sizes_and_reserved_words')
        nlayer=self.unpack('H',258)[0]
        if not nlayer:self.fail('MacDraw II header has no layer table; no native drawing can be recovered')
        # Header counts use ruler, pen, FONT, arrow, DASH order; storage
        # extents use ruler, pen, dash, arrow, font order.
        stored_counts=self.unpack('5H',260)
        count_order=(0,1,4,3,2)
        counts=tuple(stored_counts[k] for k in count_order)
        sizes=self.unpack('5I',416)+self.unpack('8I',456)
        pos=500;zones=[]
        for name,size in zip(ZONE_NAMES,sizes):
            if pos+size>len(raw):self.fail(f'0x{pos:x}: MacDraw II {name} zone exceeds file')
            zones.append((pos,size));self.span(pos,size,name);pos+=size
        self.header['zones']=[dict(name=name,offset=a,length=n) for name,(a,n) in zip(ZONE_NAMES,zones)]
        tables=[]
        for k,(a,n) in enumerate(zones[:5]):
            size=STYLE_SIZES[k]
            if n%size:self.fail(f'0x{a:x}: incomplete MacDraw II {ZONE_NAMES[k]} table record')
            if counts[k]!=n//size:
                self.problem(260+2*count_order[k],2,'style_count',f'{ZONE_NAMES[k]} count differs from table extent',True)
            table=[]
            for p in range(a,a+n,size):
                if k==0:entry=self.unpack('IddHH',p)
                elif k==1:entry=self.unpack('IIHH',p)
                elif k==2:entry=self.unpack('I6i',p)
                elif k==3:entry=self.unpack('I H 2i',p)
                else:entry=self.unpack('4H2BH3H',p)
                table.append(entry)
            tables.append(table)
        self.pens=[(e[1]/65536,e[2],e[3]) for e in tables[1]]
        self.dashes=[[v/65536 for pair in zip(e[1::2],e[2::2]) if any(pair) for v in pair] for e in tables[2]]
        self.font_styles=[]
        for e in tables[4]:
            uses,height,ascent,family,face,pad,size,red,green,blue=e
            self.font_styles.append(dict(font_id=family,face=face,size=size,height=height,ascent=ascent,
                                         color=f'#{red>>8:02x}{green>>8:02x}{blue>>8:02x}'))
        a,n=zones[5];names,nn=zones[6]
        if nlayer*128>n:self.fail(f'0x{a:x}: layer table shorter than layer count')
        layers=[];total=0
        for i in range(nlayer):
            p=a+128*i
            flags,ident,name_ref,count=self.unpack('2H2I',p,p+128)
            label=''
            if name_ref<nn:
                size=raw[names+name_ref]
                if name_ref+1+size<=nn:label=raw[names+name_ref+1:names+name_ref+1+size].decode('mac_roman')
            layers.append(dict(index=i+1,flags=flags,id=ident,name=label,count=count,first=total));total+=count
        self.header['layers']=layers
        self.header['library_count']=self.unpack('H',298)[0]
        def recover_pool(zone):
            try:return self.pool(zone)
            except self.api.FormatError as error:
                self.problem(zone[0],zone[1],'heap',str(error)+'; references to this heap cannot be resolved',True)
                return {}
        self.layer_library=recover_pool(zones[7])
        self.geometry=recover_pool(zones[10]);self.texts=recover_pool(zones[11])
        available=(len(raw)-pos)//32
        if total>available:
            self.problem(pos,len(raw)-pos,'object_table',f'{total} object records declared; only {available} complete records remain',True)
            total=available
        flat=[]
        for i in range(total):
            p=pos+32*i;self.span(p,32,'object_record')
            try:flat.append(self.object(p,i))
            except (self.api.FormatError,mt.FontError,OverflowError) as error:
                self.problem(p,32,'object',str(error)+'; object omitted',True)
                self.spans[-1]=(p,32,'recovery_uninterpreted_bytes')
                flat.append(None)
        end=pos+32*total
        self.span(end,len(raw)-end,'unreferenced_trailing_storage')
        self.header['unreferenced_trailing_storage']=dict(offset=end,length=len(raw)-end)
        objects=[]
        for layer in layers:
            roots=[];stack=[]
            for obj in flat[layer['first']:layer['first']+layer['count']]:
                if obj is None:continue
                kind=obj.fields['file_kind']
                if kind==11:
                    if stack:
                        group=stack.pop()
                        expected=obj.offset+32-group.offset
                        if group.fields['reference']!=expected:
                            self.problem(group.offset+26,2,'group_size','group byte count disagrees with matching end record',True)
                    else:self.problem(obj.offset,32,'group_end','unmatched group-end record',True)
                    continue
                (stack[-1].children if stack else roots).append(obj)
                if kind==10 and not obj.fields['flags']&64:stack.append(obj)
            if stack:self.problem(stack[0].offset,32,'group_end','missing group-end record; retained group children',True)
            def count_tree(obj):
                obj.count=1+sum(count_tree(child) for child in obj.children)
                return obj.count
            for obj in roots:
                count_tree(obj);obj.fields['layer']=layer
            objects.extend(roots)
        if not objects and total:self.fail('MacDraw II contains no recoverable drawing objects')
        self.header['record_count']=total
        self.header['text_environment_override']=dict(mt.TEXT_ENVIRONMENT,macdraw_revision='II',
            first_baseline='saved per-line ascent',line_breaks='saved character-offset table',
            missing_family_substitution='Geneva, retaining the stored point size and saved line positions')
        self.header['metadata_limitations_override']=[
            'MacDraw II printer/editor state, heap free-list semantics, library state and unreferenced storage are not completely decoded.',
            'Missing resource-fork custom pattern definitions use explicit recovery substitutions; the original source is embedded unchanged.']
        self.spans.sort()
        doc=self.api.Document(raw,'II:'+str(subversion),self.header,objects,self.spans,self.issues,total)
        doc.audit();return doc

    def resolve_paint(self,value,offset):
        if value==0:return 'none'
        if value&0xc000==0x4000 and 1<=value&0x3fff<=len(COLORS):return COLORS[(value&0x3fff)-1]
        if not value&0xc000 and 1<=value<=len(PATTERNS):return PATTERNS[value-1]
        self.problem(offset,2,'pattern_resource',f'pattern/color {value:#x} needs an unavailable custom resource; using black')
        return '#000000'

    def object(self,p,index):
        a=self.api
        box=self.fixed_box(p,p+32)
        flags,typ,state,pen,outline,fill,dash,aux,reference,tail=self.unpack('4B2H2BHI',p+16,p+32)
        kind=typ&15
        if not 1<=kind<=11:self.fail(f'0x{p:x}: unknown MacDraw II object type {kind}')
        if flags&128 and not flags&64:self.fail(f'0x{p:x}: rotation flag requires an object-data block')
        o=a.Object(p,kind,(0,0,2,3,1,0),end=p+32)
        f=o.fields
        f.update(native2=True,file_kind=kind,box=box,source_box=box,flags=flags,type_flags=typ,
                 state=state,aux=aux,reference=reference,tail=tail)
        if kind in (10,11) and not flags&64:return o
        width=1
        if pen:
            if pen<=len(self.pens):
                logical,vertical,horizontal=self.pens[pen-1]
                width=(vertical+horizontal)/2
                if abs(logical-width)>1/65536:
                    self.problem(p+19,1,'pen_scaling','logical pen width differs from its saved QuickDraw dimensions; using saved drawing-space dimensions')
                if vertical!=horizontal:
                    self.problem(p+19,1,'rectangular_pen','unequal QuickDraw pen dimensions use their mean SVG stroke width')
            else:self.problem(p+19,1,'pen',f'undefined pen {pen}; using one point')
        f.update(stroke=self.resolve_paint(outline,p+20),fill=self.resolve_paint(fill,p+22),width=width)
        if dash:
            if dash<=len(self.dashes):f['dash']=self.dashes[dash-1]
            else:self.problem(p+24,1,'dash',f'undefined dash pattern {dash}; using a solid line')
        if not flags&64:
            if kind==4:
                radius=self.unpack('i',p+25,p+32)[0]/65536/36
                f['radius']=radius if radius>0 else 25
                self.problem(p+25,4,'rounded_corner','rounded-rectangle corner units are not verified; using the documented radius conversion profile')
            if kind not in (2,3,4,5):self.fail(f'0x{p:x}: type {kind} requires an object-data block')
            return o
        if reference<8 or reference%4:self.fail(f'0x{p+26:x}: invalid object-data handle')
        try:start,end=self.geometry[(reference-8)//4]
        except KeyError:self.fail(f'0x{p+26:x}: missing object-data handle {reference:#x}')
        self.used_blocks.add((start,end))
        first,second=self.unpack('2H',start+8,end);cursor=start+12
        f.update(data_offset=start,data_length=end-start,extra_fields=(first,second))
        if flags&128:
            angle=self.unpack('i',cursor,end)[0]/65536
            local=self.fixed_box(cursor+4,end);pivot=self.unpack('2i',cursor+20,end)
            f['rotation']=dict(angle=angle,local_box=local,pivot=tuple(v/65536 for v in pivot))
            cursor+=28
        if kind in (1,10):
            cursor=self.text_object(o,cursor,end,second,kind==10)
        elif kind in (7,8):
            if (end-cursor)%8:self.fail(f'0x{cursor:x}: partial polygon vertex')
            vertices=[self.unpack('2i',q,end) for q in range(cursor,end,8)]
            if not vertices:self.fail('empty MacDraw II polygon')
            f['points']=[(box[1]+x/65536,box[0]+y/65536) for y,x in vertices]
            cursor=end
            if kind==7:self.problem(start,end-start,'smooth_curve','freehand smoothing uses the documented legacy spline profile; MacDraw II interpolation is not verified')
        elif kind==9:
            src=self.unpack('4h',cursor,end);handle,row=self.unpack('IH',cursor+8,end)
            bounds=self.unpack('4h',cursor+14,end);top,left,bottom,right=bounds
            st,sl,sb,sr=src
            if not (0<row<0x4000 and 0<right-left<=row*8 and top<=st<sb<=bottom and left<=sl<sr<=right):self.fail('invalid MacDraw II monochrome bitmap bounds')
            pixels=cursor+22;need=row*(bottom-top)
            if pixels+need>end:self.fail('truncated MacDraw II bitmap')
            f.update(source_rect=src,bitmap_bounds=bounds,row_bytes=row,bitmap=self.data[pixels:pixels+need])
            cursor=pixels+need
        elif kind==2:
            angle=self.unpack('i',cursor,end)[0]/65536
            ends=self.fixed_box(cursor+4,end)
            f.update(line_angle=angle,line_local_ends=ends,arrow_flags=second)
            cursor+=20;arrows=[]
            for bit in (1,2):
                if second&bit:
                    pts=[self.unpack('2i',cursor+8*j,end) for j in range(3)]
                    arrows.append((bit,[(box[1]+x/65536,box[0]+y/65536) for y,x in pts]));cursor+=24
            f['arrows']=arrows
            if second&~7:self.problem(start+10,2,'line_flags',f'unknown line flags {second:#x}; rendering the decoded shaft and arrows')
            if second&4:
                f['measure_box']=self.fixed_box(cursor,end)
                if cursor+44>end:self.fail('truncated MacDraw II dimension label')
                size=self.data[cursor+18]
                if size>25 or cursor+44>end:self.fail('invalid MacDraw II dimension label')
                f['measure']=self.data[cursor+19:cursor+19+size]
                self.problem(cursor,44,'dimension_font','dimension-label font is not stored in the object; using Geneva 9')
                # Label coordinates are relative to the drawing object's origin.
                bt,bl,bb,br=f['measure_box'];f['measure_box']=(box[0]+bt,box[1]+bl,box[0]+bb,box[1]+br)
                metrics=self.fonts.resolve(3,9,0)
                bt,bl,bb,br=f['measure_box']
                f['text_fragments']=[dict(font_id=3,font_index=0,face=0,color='#000000',
                    text_layout=mt.Layout(metrics,f['measure_box'],bb-bt,[((bl+br-metrics.width(f['measure']))/2,bt+metrics.ascent,f['measure'])]))]
                cursor+=44
        elif kind==6:
            start_angle,sweep=self.unpack('2i',cursor,end)
            f.update(start_angle=start_angle/65536,sweep_angle=sweep/65536,
                     arc_endpoints=self.fixed_box(cursor+8,end),ellipse_local_box=self.fixed_box(cursor+24,end))
            cursor+=40
            if flags&128:
                f['cached_ellipse_points']=[self.unpack('2i',cursor+8*j,end) for j in range(8)]
                cursor+=64
        elif kind in (4,5):
            if flags&128:
                npoints=16 if kind==4 else 8
                f['cached_curve_points']=[self.unpack('2i',cursor+8*j,end) for j in range(npoints)]
                cursor+=8*npoints
        if kind==4:
            f['radius']=(first*65536+second)/4096
            self.problem(start+8,4,'rounded_corner','rotated rounded-rectangle corner interpretation is not verified; using the documented radius conversion profile')
        if end-cursor>3:
            self.problem(cursor,end-cursor,'object_extension','object-data extension has no established drawing interpretation; decoded geometry retained')
        f['allocation_padding']=self.data[cursor:end].hex()
        return o

    def text_object(self,obj,cursor,end,reference,note):
        f=obj.fields
        if reference<8 or reference%4:self.fail('invalid MacDraw II text handle')
        try:beg,stop=self.texts[(reference-8)//4]
        except KeyError:self.fail('missing MacDraw II character block')
        mode,spacing,justify_flags,align,n,nlines,nruns=self.unpack('4b3H',cursor,end)
        cursor+=10
        if note:
            self.unpack('68s',cursor,end)
            f['note_metadata']=self.data[cursor:cursor+68].hex()
            self.problem(cursor,68,'note_appearance','note text is retained; native sticky-note window decoration and author/date presentation are not reproduced')
            cursor+=68
        breaks=self.unpack(f'{nlines+1}H',cursor,end);cursor+=2*(nlines+1)
        runs=[self.unpack('Hh',cursor+4*i,end) for i in range(nruns+1)];cursor+=4*(nruns+1)
        line_metrics=[self.unpack('2H',cursor+4*i,end) for i in range(nlines+1)]
        cursor+=4*(nlines+1)
        chars=self.data[beg+8:min(stop,beg+8+n)]
        if len(chars)!=n:self.problem(beg,stop-beg,'text_length','character payload is truncated',True)
        if b'\t' in chars:
            self.problem(beg+8,len(chars),'tab_stops','tab-stop spacing is not stored in the decoded text record; using 36-point stops from the text-box left edge')
        if not breaks or breaks[0]!=0 or list(breaks)!=sorted(breaks) or breaks[-1]>len(chars):self.fail('invalid MacDraw II line-offset table')
        if not runs or runs[0][0]!=0 or [r[0] for r in runs]!=sorted(r[0] for r in runs):self.fail('invalid MacDraw II font-run table')
        if align not in (-1,0,1,2):
            self.problem(obj.offset,32,'text_alignment',f'unknown alignment {align}; using left alignment')
            align=0
        f.update(text_bytes=chars,text_mode=(mode,spacing,justify_flags,align),line_breaks=breaks,
                 line_metrics=line_metrics,font_runs=runs,text_fragments=[])
        original=f['box']
        if 'rotation' in f:
            lt,ll,lb,lr=f['rotation']['local_box'];t,l,_,_=original
            original=(t+lt,l+ll,t+lb,l+lr)
        top,left,bottom,right=original
        positions=[v[0] for v in runs]
        def font_at(index):
            run=bisect_right(positions,index)-1;ident=runs[max(0,run)][1]
            if not 0<=ident<len(self.font_styles):self.fail('text references undefined font style')
            style=self.font_styles[ident]
            if style['size']<1 or style['size']>4096:self.fail('invalid MacDraw II point size')
            metrics=self.fonts.resolve(style['font_id'],style['size'],style['face']&127)
            return ident,style,metrics
        def chunks(start,stop):
            at=start
            while at<stop:
                ident,style,metrics=font_at(at)
                nxt=min([v for v in positions if v>at]+[stop]);nxt=min(nxt,stop)
                yield at,nxt,ident,style,metrics
                at=nxt
        line_starts=list(breaks)
        if line_starts[-1]<len(chars):line_starts.append(len(chars))
        y=top
        for i,(start,stop) in enumerate(zip(line_starts,line_starts[1:])):
            content_stop=stop
            while content_stop>start and chars[content_stop-1]==13:content_stop-=1
            pieces=list(chunks(start,content_stop))
            # Build positions before alignment, keeping tab controls out of
            # glyph data. Font runs may split a line or a tab-delimited field.
            width=0;segments=[]
            for a,b,ident,style,m in pieces:
                for j,segment in enumerate(chars[a:b].split(b'\t')):
                    if j:width=(math.floor(width/36)+1)*36
                    if segment:segments.append((width,segment,ident,style,m))
                    width+=m.width(segment)
            x=left if align==0 else left+(right-left-width)/2 if align==1 else right-width if align==-1 else left
            height,ascent=line_metrics[min(i,len(line_metrics)-1)]
            if not height:height=max((m.ascent+m.descent+m.leading for *_,m in pieces),default=12)
            if not ascent:ascent=max((m.ascent for *_,m in pieces),default=9)
            # Full justification expands literal spaces on non-final soft lines.
            spaces=chars[start:content_stop].count(b' ')
            extra=max(0,right-left-width)/spaces if align==2 and spaces and stop<len(chars) and (stop==0 or chars[stop-1]!=13) else 0
            origin=x;expanded=0
            for at,raw,ident,style,m in segments:
                x=origin+at+expanded
                glyph_segments=[raw] if not extra else [bytes((c,)) for c in raw]
                for segment in glyph_segments:
                    fragment=dict(font_id=style['font_id'],font_index=ident+1,face=style['face'],color=style['color'],
                                  text_layout=mt.Layout(m,original,height,[(x,y+ascent,segment)]))
                    f['text_fragments'].append(fragment)
                    x+=m.width(segment)+extra*segment.count(b' ')
                    expanded+=extra*segment.count(b' ')
            y+=height
        f['text_box']=original
        return cursor


def parse(data,api,*,fonts=None,recover=False,require_complete=False):
    return Decoder(api,data,fonts,recover,require_complete).parse()


def paint(renderer,value):
    api=sys.modules[type(renderer).__module__]
    if value=='none' or value.startswith(('#','url(#')):return value
    if value=='0000000000000000':return '#ffffff'
    if value=='ffffffffffffffff':return '#000000'
    ident='md2-pattern-'+value
    if not hasattr(renderer,'md2_patterns'):renderer.md2_patterns=set()
    if ident not in renderer.md2_patterns:
        renderer.md2_patterns.add(ident)
        pat=api.element(renderer.defs,'pattern',id=ident,width=8,height=8,patternUnits='userSpaceOnUse')
        api.element(pat,'rect',width=8,height=8,fill='white')
        pts=[(x,y) for y,row in enumerate(bytes.fromhex(value)) for x in range(8) if row&(128>>x)]
        api.element(pat,'path',d=mt.pixel_path(pts),fill='black')
    return 'url(#'+ident+')'


def xml_text(raw):
    text=raw.decode('mac_roman') if isinstance(raw,bytes) else raw
    return ''.join('⌘' if ord(c)==17 else c if ord(c)>=32 or c in '\t\r\n' else '�' for c in text)


def render_text(renderer,g,fragments,rotation=None,origin=(0,0)):
    api=sys.modules[type(renderer).__module__];E=api.element;num=api.number
    for frag in fragments:
        layout=frag['text_layout'];m=layout.metrics
        for x,y,chars in layout.lines:
            for at in range(0,len(chars),13 if m.shadow else 34):
                text=chars[at:at+(13 if m.shadow else 34)]
                black,white=m.pixels(text)
                key=(m.strike.digest,m.face,text,frag['color'])
                if not hasattr(renderer,'md2_glyphs'):renderer.md2_glyphs={}
                if key not in renderer.md2_glyphs:
                    ident='md2-text-'+str(len(renderer.md2_glyphs));renderer.md2_glyphs[key]=ident
                    group=E(renderer.defs,'g',id=ident,shape_rendering='crispEdges')
                    if white:E(group,'path',d=mt.pixel_path(white),fill='white')
                    if black:E(group,'path',d=mt.pixel_path(black),fill=frag['color'])
                use=E(g,'use',transform=f'translate({num(x)} {num(y)}) scale({num(m.numer/256)})')
                use.set('{'+api.XLINK+'}href','#'+renderer.md2_glyphs[key])
                pixels=black|white
                if pixels:
                    xs,ys=zip(*pixels);scale=m.numer/256
                    corners=[(x+xx*scale,y+yy*scale) for xx,yy in ((min(xs),min(ys)),(max(xs)+1,min(ys)),(max(xs)+1,max(ys)+1),(min(xs),max(ys)+1))]
                    if rotation:
                        lt,ll,lb,lr=rotation['local_box'];oy,ox=origin
                        cx=ox+(ll+lr)/2;cy=oy+(lt+lb)/2
                        co=math.cos(rotation['angle']);si=math.sin(rotation['angle'])
                        corners=[(cx+co*(xx-cx)-si*(yy-cy),cy+si*(xx-cx)+co*(yy-cy)) for xx,yy in corners]
                    xs,ys=zip(*corners);renderer.add_bounds((min(ys),min(xs),max(ys),max(xs)))
                x+=m.width(text)


def render(renderer,parent,obj):
    api=sys.modules[type(renderer).__module__];E=api.element;num=api.number
    f=obj.fields;k=f['file_kind'];t,l,b,r=f['box']
    layer=f.get('layer')
    if layer and renderer.layer is not None and renderer.layer!=layer['index']:return
    g=E(parent,'g',data_source_offset=obj.offset,data_macdraw_ii_type=k)
    if layer:
        g.set('data-layer',xml_text(layer['name']))
        if layer['flags']&0x8000 and renderer.layer is None:
            g.set('display','none')
            saved_bounds=renderer.bounds
            renderer.bounds=[]
            # The hidden artwork is retained in the SVG, but must not enlarge
            # its visible canvas. Layer exports can display it independently.
            clone=api.Object(obj.offset,obj.kind,obj.attrs,dict(f),obj.children,obj.end,obj.count)
            clone.fields.pop('layer',None)
            render(renderer,g,clone)
            renderer.bounds=saved_bounds
            return
    if k==10 and not f['flags']&64:
        for child in obj.children:render(renderer,g,child)
        return
    if k==11:return
    attrs=dict(stroke=paint(renderer,f['stroke']),fill=paint(renderer,f['fill']),stroke_width=num(f['width']),
               stroke_linejoin='round',stroke_linecap='square',fill_rule='evenodd')
    if f.get('dash'):attrs['stroke_dasharray']=' '.join(num(v) for v in f['dash'])
    rotation=f.get('rotation')
    shape_box=f['box']
    if rotation and k not in (7,8):
        lt,ll,lb,lr=rotation['local_box'];shape_box=(t+lt,l+ll,t+lb,l+lr)
        cx=l+(ll+lr)/2;cy=t+(lt+lb)/2
        g.set('transform',f'rotate({num(math.degrees(rotation["angle"]))} {num(cx)} {num(cy)})')
    tt,ll,bb,rr=shape_box
    # Empty QuickDraw rectangles have no drawing extent. Retain their records
    # in the source metadata, but do not enlarge the SVG to include them.
    if k in (3,4,5,9) and (rr<=ll or bb<=tt):return
    renderer.add_bounds(f['box'])
    if k in (1,10):
        if attrs['fill']!='none':E(g,'rect',x=num(ll),y=num(tt),width=num(max(0,rr-ll)),height=num(max(0,bb-tt)),fill=attrs['fill'])
        E(g,'title').text=xml_text(f['text_bytes'])
        render_text(renderer,g,f['text_fragments'],rotation,(t,l))
    elif k==2:
        fx=bool(f['type_flags']&32);fy=bool(f['type_flags']&64)
        # The inline rectangle encloses the square pen. The data-block
        # rectangle instead encloses the path endpoints themselves.
        bt,bl,bb,br=f.get('line_local_ends',(0,0,max(0,b-t-f['width']),max(0,r-l-f['width'])))
        g.set('transform',f'translate({num(f["width"]/2)} {num(f["width"]/2)})')
        x1,x2=(br,bl) if fx else (bl,br);y1,y2=(bb,bt) if fy else (bt,bb)
        endpoints=[(l+x1,t+y1),(l+x2,t+y2)];shaft=list(endpoints)
        for bit,arrow in f.get('arrows',[]):
            at=bit-1;shaft[at]=arrow[1]
            points=[arrow[0],endpoints[at],arrow[2]]
            E(g,'path',d='M'+' L'.join(f'{num(x)} {num(y)}' for x,y in points)+' Z',fill=attrs['stroke'],stroke='none')
        E(g,'line',x1=num(shaft[0][0]),y1=num(shaft[0][1]),x2=num(shaft[1][0]),y2=num(shaft[1][1]),**dict(attrs,fill='none'))
        if f.get('measure'):
            bt,bl,bb,br=f['measure_box']
            E(g,'rect',x=num(bl),y=num(bt),width=num(br-bl),height=num(bb-bt),fill='white')
            render_text(renderer,g,f['text_fragments'])
    elif k in (3,4):
        if rr>=ll and bb>=tt:
            extra=dict(rx=num(min(f.get('radius',25),(rr-ll)/2)),ry=num(min(f.get('radius',25),(bb-tt)/2))) if k==4 else {}
            E(g,'rect',x=num(ll),y=num(tt),width=num(rr-ll),height=num(bb-tt),**attrs,**extra)
    elif k==5:
        E(g,'ellipse',cx=num((ll+rr)/2),cy=num((tt+bb)/2),rx=num(max(0,(rr-ll)/2)),ry=num(max(0,(bb-tt)/2)),**attrs)
    elif k==6:
        at,al,ab,ar=f['ellipse_local_box']
        proxy=api.Object(obj.offset,7,obj.attrs,dict(box=(t+at,l+al,t+ab,l+ar),start_angle=f['start_angle'],sweep_angle=f['sweep_angle']))
        renderer.arc(g,proxy,attrs)
    elif k in (7,8):
        points=f['points']
        if k==7 and len(points)>=3:
            points=[(x/65536,y/65536) for x,y in api.spline_vertices([(round(x*65536),round(y*65536)) for x,y in points],False)]
        closed=len(points)>1 and points[0]==points[-1]
        E(g,'path',d='M'+' L'.join(f'{num(x)} {num(y)}' for x,y in points)+(' Z' if closed else ''),**attrs)
    elif k==9:
        import base64
        href='data:image/png;base64,'+base64.b64encode(api.png_bitmap(obj)).decode('ascii')
        im=E(g,'image',x=num(ll),y=num(tt),width=num(max(0,rr-ll)),height=num(max(0,bb-tt)),preserveAspectRatio='none')
        im.set('{'+api.XLINK+'}href',href)
