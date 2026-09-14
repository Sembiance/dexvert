# Vibe coded by Codex
"""MacDraw Pro data-fork decoder. See macDraw.txt for fidelity boundaries.

Uses the project's shared heap reader and basic SVG shape renderer. Pro's
record layouts, typed control vertices, text and resources are decoded here.
Only Python's standard library and the companion macDraw modules are used.
"""
from __future__ import annotations
import base64
import colorsys
import hashlib
import math
import struct
import sys
import zlib
from bisect import bisect_right
import macDrawII as ii
import macDrawText as mt

STYLE_SIZES=(24,12,28,14,22,238)
ZONE_NAMES=('rulers','pens','dashes','arrows','fonts','paragraphs','layers','layer_names',
            'layer_libraries','libraries','library_names','geometry_heap','text_heap','free_storage')

class Decoder(ii.Decoder):
    def __init__(self,api,data,fonts,recover,require_complete,resource_fork=None):
        super().__init__(api,data,fonts,recover,require_complete)
        self.header['native_format']='MacDraw Pro'
        self.resource_fork=resource_fork
        self.resources={}
        self.once=set()
        self.metric_cache={}

    def fail(self,message):
        raise self.api.FormatError(message.replace('MacDraw II','MacDraw Pro'))

    def unpack(self,fmt,offset,end=None):
        n=struct.calcsize('>'+fmt)
        if offset<0 or offset+n>min(len(self.data),len(self.data) if end is None else end):
            self.fail(f'0x{offset:x}: truncated MacDraw Pro {fmt} field')
        return struct.unpack_from('>'+fmt,self.data,offset)

    def span(self,offset,length,name):
        if length:self.spans.append((offset,length,'macdrawpro_'+name))

    def problem(self,offset,length,code,detail,damage=False):
        if self.require_complete or (damage and not self.recover):self.fail(f'0x{offset:x}: {detail}')
        self.issues.append(self.api.Issue(offset,length,('recovery_' if damage else '')+'macdrawpro_'+code,detail))

    def warn_once(self,offset,length,code,key,detail):
        if (code,key) in self.once:return
        self.once.add((code,key));self.problem(offset,length,code,detail)

    def parse(self):
        raw=self.data
        if len(raw)<468:self.fail('truncated MacDraw Pro header')
        signature=raw[:8]
        if signature[:4] not in (b'dDoc',b'dLib') or signature[4:] not in (b'D2\xff\xff',):
            self.fail('unsupported MacDraw Pro signature/subversion')
        subversion=self.unpack('h',6)[0]
        self.header.update(subversion=subversion,stationery=signature[:4]==b'dLib')
        self.span(0,8,'signature');self.span(8,120,'printing_record')
        self.span(128,128,'editor_preferences')
        self.span(256,148,'counts_and_saved_rectangles')
        self.span(404,64,'zone_sizes_and_saved_state')
        self.read_resources()
        nlayer=self.unpack('H',258)[0]
        if not nlayer:self.fail('MacDraw Pro header has no layer table; no native drawing can be recovered')
        stored_counts=self.unpack('6H',260)
        count_order=(0,1,5,4,2,3)
        counts=tuple(stored_counts[k] for k in count_order)
        sizes=self.unpack('14I',404)
        pos=468;zones=[]
        for name,size in zip(ZONE_NAMES,sizes):
            if pos+size>len(raw):self.fail(f'0x{pos:x}: MacDraw Pro {name} zone exceeds file')
            zones.append((pos,size));self.span(pos,size,name);pos+=size
        self.header['zones']=[dict(name=name,offset=a,length=n) for name,(a,n) in zip(ZONE_NAMES,zones)]
        tables=[]
        for k,(a,n) in enumerate(zones[:6]):
            size=STYLE_SIZES[k]
            if n%size:self.fail(f'0x{a:x}: incomplete MacDraw Pro {ZONE_NAMES[k]} table record')
            if counts[k]!=n//size:
                self.problem(260+2*count_order[k],2,'style_count',f'{ZONE_NAMES[k]} count differs from table extent',True)
            table=[]
            for p in range(a,a+n,size):
                if k==0:entry=self.unpack('IddHH',p)
                elif k==1:entry=self.unpack('IIHH',p)
                elif k==2:entry=self.unpack('I6i',p)
                elif k==3:entry=self.unpack('I H 2i',p)
                elif k==4:entry=self.unpack('Hii6H',p)
                else:entry=self.unpack('238s',p)[0]
                table.append(entry)
            tables.append(table)
        self.pens=[(e[1]/65536,e[2],e[3]) for e in tables[1]]
        self.dashes=[[v/65536 for pair in zip(e[1::2],e[2::2]) if any(pair) for v in pair] for e in tables[2]]
        self.font_styles=[]
        for i,e in enumerate(tables[4]):
            uses,height,ascent,family,face,size,back,state,color=e
            self.font_styles.append(dict(font_id=family,face=face,size=size/4,height=height/65536,
                ascent=ascent/65536,color_ref=color,offset=zones[4][0]+22*i,back=back,state=state))
        self.paragraphs=[self.paragraph(e) for e in tables[5]]
        a,n=zones[6];names,nn=zones[7]
        if nlayer*130>n:self.fail(f'0x{a:x}: layer table shorter than layer count')
        layers=[];total=0
        for i in range(nlayer):
            p=a+130*i
            flags,ident,name_ref,count=self.unpack('2H2I',p,p+130)
            label=''
            if name_ref<nn:
                size=raw[names+name_ref]
                if name_ref+1+size<=nn:label=raw[names+name_ref+1:names+name_ref+1+size].decode('mac_roman')
            layers.append(dict(index=i+1,flags=flags,id=ident,name=label,count=count,first=total));total+=count
        self.header['layers']=layers
        self.header['library_count']=self.unpack('H',286)[0]
        def recover_pool(zone):
            try:return self.pool(zone)
            except self.api.FormatError as error:
                self.problem(zone[0],zone[1],'heap',str(error)+'; references to this heap cannot be resolved',True)
                return {}
        self.layer_library=recover_pool(zones[8])
        self.geometry=recover_pool(zones[11]);self.texts=recover_pool(zones[12])
        available=(len(raw)-pos)//34
        if total>available:
            self.problem(pos,len(raw)-pos,'object_table',f'{total} object records declared; only {available} complete records remain',True)
            total=available
        flat=[]
        for i in range(total):
            p=pos+34*i;self.span(p,34,'object_record')
            try:flat.append(self.object(p,i))
            except (self.api.FormatError,mt.FontError,OverflowError) as error:
                self.problem(p,34,'object',str(error)+'; object omitted',True)
                self.spans[-1]=(p,34,'recovery_uninterpreted_bytes')
                flat.append(None)
        end=pos+34*total
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
                    else:self.problem(obj.offset,34,'group_end','unmatched group-end record',True)
                    continue
                (stack[-1].children if stack else roots).append(obj)
                if kind==10 and not obj.fields['flags']&64:stack.append(obj)
            if stack:self.problem(stack[0].offset,34,'group_end','missing group-end record; retained group children',True)
            def count_tree(obj):
                obj.count=1+sum(count_tree(child) for child in obj.children)
                return obj.count
            for obj in roots:
                count_tree(obj);obj.fields['layer']=layer
            objects.extend(roots)
        if not objects and total:self.fail('MacDraw Pro contains no recoverable drawing objects')
        self.header['record_count']=total
        self.header['text_environment_override']=dict(mt.TEXT_ENVIRONMENT,macdraw_revision='Pro',
            first_baseline='saved per-line ascent',line_breaks='saved character-offset table',
            missing_family_substitution='Geneva, retaining the stored point size and saved line positions')
        self.header['metadata_limitations_override']=[
            'Pro printer/editor state, allocation bookkeeping, libraries, unused style entries and trailing storage are framed and preserved but not completely interpreted.',
            'Custom paints and bitmap palettes require the document resource fork; missing definitions use explicitly reported substitutions.',
            'Pro typography uses original bitmap font resources and saved line positions; outline-font fractional advances, tracking and some paragraph effects are not exact.']
        self.spans.sort()
        doc=self.api.Document(raw,'Pro:'+str(subversion),self.header,objects,self.spans,self.issues,total)
        doc.audit();return doc

    def object(self,p,index):
        a=self.api
        box=self.fixed_box(p,p+34)
        flags,typ,state,pen,extra,outline,fill,dash,aux,reference,stroke_color,fill_color=self.unpack('4B3HBb3H',p+16,p+34)
        kind=typ&15
        if not 1<=kind<=12:self.fail(f'0x{p:x}: unknown MacDraw Pro object type {kind}')
        if flags&128 and not flags&64:self.fail(f'0x{p:x}: rotation flag requires an object-data block')
        o=a.Object(p,kind,(0,0,2,3,1,0),end=p+34)
        f=o.fields
        f.update(native_pro=True,file_kind=kind,box=box,source_box=box,flags=flags,type_flags=typ,
                 state=state,aux=aux,reference=reference,extra_state=extra,pattern_ids=(outline,fill),color_ids=(stroke_color,fill_color))
        if kind in (10,11) and not flags&64:return o
        width=1
        if pen:
            if pen<=len(self.pens):
                logical,vertical,horizontal=self.pens[pen-1]
                width=logical
                if width<0 or not math.isfinite(width):self.fail('invalid Pro logical pen width')
                if vertical!=horizontal:
                    self.warn_once(p+19,1,'rectangular_pen',pen,'unequal cached QuickDraw pen dimensions cannot be represented by one SVG stroke width; using the logical pen width')
            else:self.problem(p+19,1,'pen',f'undefined pen {pen}; using one point')
        f.update(stroke=self.resolve_paint(outline,stroke_color,p+22),fill=self.resolve_paint(fill,fill_color,p+24),width=width)
        f['paint_substitutions']=dict(stroke=self.paint_missing(outline,stroke_color),fill=self.paint_missing(fill,fill_color))
        # Missing paints must not turn a many-object drawing into an opaque
        # black rectangle. This constant, explicitly reported inspection
        # profile exposes boundaries; it does not guess the missing palette.
        if f['paint_substitutions']['stroke']:f['stroke']='#808080'
        if f['paint_substitutions']['fill']:
            f['fill']='#888888'
            if f['stroke']=='none' or f['paint_substitutions']['stroke']:
                f['stroke']='#303030'
                if not outline:f['width']=0.75
            self.warn_once(p+22,12,'paint_preview',0,
                'unresolved fill paints use a neutral-gray geometry preview with contrasting outlines; these are inspection colors, not recovered original colors')
        if dash:
            if dash<=len(self.dashes):f['dash']=self.dashes[dash-1]
            else:self.problem(p+26,1,'dash',f'undefined dash pattern {dash}; using a solid line')
        if not flags&64:
            if kind==4:
                radius=self.unpack('i',p+27,p+34)[0]/65536/36
                f['radius']=radius if radius>0 else 25
                self.problem(p+27,4,'rounded_corner','rounded-rectangle corner units are not verified; using the documented radius conversion profile')
            if kind not in (2,3,4,5):self.fail(f'0x{p:x}: type {kind} requires an object-data block')
            return o
        if reference<8 or reference%4:self.fail(f'0x{p+28:x}: invalid object-data handle')
        try:start,end=self.geometry[(reference-8)//4]
        except KeyError:self.fail(f'0x{p+28:x}: missing object-data handle {reference:#x}')
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
        elif kind in (7,8,9):
            cursor=self.path_object(o,cursor,end)
        elif kind==12:
            cursor=self.bitmap_object(o,cursor,end)
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
                if cursor+44>end:self.fail('truncated MacDraw Pro dimension label')
                size=self.data[cursor+18]
                if size>25 or cursor+44>end:self.fail('invalid MacDraw Pro dimension label')
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

    def read_resources(self):
        self.colors=[];self.patterns=[];self.gradients=[];self.cluts={}
        self.color_notes=[]
        if not self.resource_fork:
            self.header['drawing_resources']=dict(present=False,resources=[])
            return
        try:
            entries=mt.read_resources(self.resource_fork)
        except mt.FontError as error:
            self.problem(0,8,'resource_fork',str(error)+'; resource definitions unavailable',True)
            self.header['drawing_resources']=dict(present=True,valid=False)
            return
        self.resources={(tag,rid):raw for tag,rid,name,raw in entries}
        self.header['drawing_resources']=dict(present=True,valid=True,
            bytes=len(self.resource_fork),sha256=hashlib.sha256(self.resource_fork).hexdigest(),
            resources=[dict(type=tag.decode('mac_roman'),id=rid,name=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
                       for tag,rid,name,raw in entries])
        # Palette map record count and stride are independently declared by
        # PaDB. An empty map is represented by a ten-byte placeholder.
        for tag,rid,stride in ((b'DPCo',0,20),(b'DPPa',1,18),(b'DPRa',2,56)):
            raw=self.resources.get((tag,rid))
            if raw is None:continue
            definition=self.resources.get((b'PaDB',rid))
            count=None
            if definition is not None and len(definition)==80:
                map_tag,record_size,count=struct.unpack_from('>4sHH',definition,48)
                if map_tag!=tag or record_size!=stride:
                    self.warn_once(0,8,'resource_layout',tag,f'{tag.decode()} palette descriptor is unsupported; map unavailable')
                    continue
            if count==0 or (count is None and len(raw)==10):
                if len(raw) not in (0,10):self.warn_once(0,8,'resource_layout',tag,'empty palette has unexplained storage')
                continue
            if len(raw)%stride or (count is not None and count*stride!=len(raw)):
                self.warn_once(0,8,'resource_layout',tag,f'{tag.decode()} record count and extent disagree; map unavailable')
                continue
            for at in range(0,len(raw),stride):
                row=raw[at:at+stride]
                if tag==b'DPCo':
                    mode=struct.unpack_from('>H',row,8)[0]
                    vals=struct.unpack_from('>4H',row,10)
                    note=None
                    if mode&3==1:color=rgb16(vals[:3])
                    elif mode&3==2:
                        c,m,y,k=(v/65535 for v in vals)
                        color=rgb_float(((1-c)*(1-k),(1-m)*(1-k),(1-y)*(1-k)))
                        note=('cmyk_profile',0,'CMYK colors use device-independent multiplicative CMYK-to-sRGB conversion; the original monitor/printing profile is unavailable')
                    elif mode&3==3:
                        h,s,l=(v/65535 for v in vals[:3]);color=rgb_float(colorsys.hls_to_rgb(h,l,s))
                        note=('hsl_profile',0,'HSL palette interpretation uses normalized components; the original application color-management profile is unavailable')
                    else:
                        note=('color_model',mode,f'unknown color model {mode}; RGB component fallback')
                        color=rgb16(vals[:3])
                    self.colors.append(color)
                    self.color_notes.append(note)
                elif tag==b'DPPa':self.patterns.append(row[10:18].hex())
                else:
                    kind=struct.unpack_from('>h',row,8)[0];selector=struct.unpack_from('>H',row,48)[0]
                    colors=[rgb16(struct.unpack_from('>3H',row,16+i*8)) for i in range(4) if selector&(0x8000>>i)]
                    self.gradients.append(dict(kind=kind,center=tuple(v/100 for v in row[10:14]),
                        offset=struct.unpack_from('>i',row,10)[0]/65536,angle=selector&4095,colors=colors))
        for (tag,rid),raw in self.resources.items():
            if tag!=b'clut':continue
            try:
                if len(raw)<8:raise ValueError('truncated color table')
                seed,flags,last=struct.unpack_from('>IHH',raw)
                count=0 if last==65535 else last+1
                if len(raw)!=8+8*count:raise ValueError('color table count and extent disagree')
                colors={}
                for i in range(count):
                    index,r,g,b=struct.unpack_from('>4H',raw,8+8*i)
                    index=i if flags&0x8000 else index
                    if index in colors:raise ValueError('duplicate color-table index')
                    colors[index]=(r>>8,g>>8,b>>8)
                self.cluts[rid]=colors
            except ValueError as error:
                self.warn_once(0,8,'bitmap_palette',rid,f'clut {rid}: {error}; neutral palette fallback')

        self.header['drawing_resources']['decoded_counts']=dict(colors=len(self.colors),
            patterns=len(self.patterns),gradients=len(self.gradients),bitmap_palettes=len(self.cluts))

    def color(self,value,offset):
        if value==0:return '#000000'
        category=value>>14;index=value&0x3fff
        if category==1:
            if index:self.warn_once(offset,2,'paper_color_bits',value,f'paper/white color {value:#06x} has unresolved low bits; white fallback')
            return '#ffffff'
        if category==2 and index<len(self.colors):
            note=self.color_notes[index]
            if note:self.warn_once(offset,2,*note)
            return self.colors[index]
        if category==3 and index<len(self.gradients):
            grad=self.gradients[index]
            if grad['colors'] and grad['kind'] not in (0,1,2):
                # The resource supplies actual colors even if its spatial
                # interpolation cannot be decoded. Keep that evidence rather
                # than classifying the whole definition as missing.
                self.warn_once(offset,2,'gradient_type',value,
                    f'gradient {index} has unsupported type {grad["kind"]}; using its first enabled color as a flat fill; remaining colors and parameters are preserved')
                return grad['colors'][0]
            if grad['colors']:
                self.warn_once(offset,2,'gradient_profile',value,'gradient colors and parameters are decoded; SVG interpolation/placement is an approximation of the original renderer')
                return dict(gradient=grad)
            self.warn_once(offset,2,'gradient_stops',value,
                f'gradient {index} has no enabled colors; neutral inspection paint')
            return '#000000'
        if category==0:
            self.warn_once(offset,2,'color_encoding',value,
                f'unsupported direct color reference {value:#06x}; neutral inspection paint (black fallback for text)')
            return '#000000'
        self.warn_once(offset,2,'missing_color',value,
            f'color/gradient {value:#06x} requires an unavailable resource definition; neutral inspection paint (black fallback for text)')
        return '#000000'

    def paint_missing(self,pattern,color):
        if not pattern or pattern==0xc005:return False
        category=color>>14;index=color&0x3fff
        if color and (category==0 or (category==2 and index>=len(self.colors)) or
                      (category==3 and (index>=len(self.gradients) or not self.gradients[index]['colors']))):
            return True
        if category==3:return False
        return pattern!=0xc006 and not (pattern>>14==2 and (pattern&0x3fff)<len(self.patterns))

    def resolve_paint(self,pattern,color,offset,*,color_offset=None):
        if pattern==0:return 'none'
        foreground=self.color(color,offset+8 if color_offset is None else color_offset)
        if pattern==0xc005:return '#ffffff'
        if pattern==0xc006 or isinstance(foreground,dict):return foreground
        if pattern>>14==2 and (pattern&0x3fff)<len(self.patterns):
            bits=self.patterns[pattern&0x3fff]
            if bits=='ffffffffffffffff':return foreground
            if bits=='0000000000000000':return '#ffffff'
            return dict(pattern=bits,foreground=foreground)
        self.warn_once(offset,2,'missing_pattern',pattern,
            f'pattern {pattern:#06x} requires an unavailable definition; solid foreground fallback')
        return foreground

    def paragraph(self,raw):
        align,reserved=struct.unpack_from('>2h',raw,2)
        left,first,right,line,before,after=(v/65536 for v in struct.unpack_from('>6i',raw,6))
        modes=struct.unpack_from('>3h',raw,30);ntabs=struct.unpack_from('>h',raw,36)[0]
        if not 0<=ntabs<=20:self.fail('invalid Pro paragraph tab count')
        tabs=[]
        for i in range(ntabs):
            kind,leader,position,decimal=struct.unpack_from('>hHiH',raw,38+10*i)
            tabs.append(dict(align=kind,leader=leader,position=position/65536,decimal=decimal))
        return dict(align=align,left=left,first=first,right=right,line=line,before=before,after=after,
                    modes=modes,tabs=tabs,reserved=reserved)

    def path_object(self,obj,cursor,end):
        count=self.unpack('H',cursor,end)[0];cursor+=2
        if not count:self.fail('empty Pro path')
        nodes=[];t,l,b,r=obj.fields['box']
        for i in range(count):
            typ=self.unpack('H',cursor,end)[0];cursor+=2
            if typ in (0,1,2,3,6,7):n=3
            elif typ in (8,9):n=1
            else:self.fail(f'0x{cursor-2:x}: unsupported Pro vertex type {typ}')
            pts=[self.unpack('2i',cursor+8*j,end) for j in range(n)];cursor+=8*n
            nodes.append((typ,[(l+x/65536,t+y/65536) for y,x in pts]))
        # The points are cached in drawing axes, including when the record
        # carries a rotation. Applying the rotation again would distort them.
        obj.fields['nodes']=nodes
        if any(typ&1 for typ,pts in nodes):
            self.warn_once(obj.offset,34,'vertex_edit_flags',0,'odd vertex tags have unresolved editing/closure bits; control points are rendered and only explicit coincident endpoints close the stroke')
        return cursor

    def bitmap_object(self,obj,cursor,end):
        f=obj.fields;src=self.unpack('4h',cursor,end)
        handle,row_word=self.unpack('IH',cursor+8,end);bounds=self.unpack('4h',cursor+14,end)
        state=self.unpack('42s',cursor+22,end)[0];pixels=cursor+64
        row=row_word&0x3fff;top,left,bottom,right=bounds;st,sl,sb,sr=src
        color=bool(row_word&0x8000)
        if color:
            version,packing,packsize,hres,vres,ptype,bits,components,component_bits,planes,table,reserved,rid,res1,res2=struct.unpack('>HHIII4HIIIh2H',state)
            if packing not in (0,1,2,3,4) or planes or ptype not in (0,16):self.fail('unsupported packed/planar Pro bitmap')
            if (ptype==0 and (bits not in (1,2,4,8) or components!=1 or component_bits!=bits)) or (ptype==16 and (bits not in (16,32) or components!=3 or component_bits not in (5,8))):
                self.fail('unsupported Pro PixMap pixel layout')
        else:bits=1;rid=None;ptype=0
        if not (row and 0<right-left and (right-left)*bits<=row*8 and top<=st<sb<=bottom and left<=sl<sr<=right):self.fail('invalid Pro bitmap bounds/row stride')
        need=row*(bottom-top)
        if pixels+need>end:self.fail('truncated Pro bitmap pixels')
        f.update(source_rect=src,bitmap_bounds=bounds,row_bytes=row,bitmap=self.data[pixels:pixels+need],
                 bitmap_header=state.hex(),pixel_bits=bits,pixel_type=ptype,color_bitmap=color,clut_id=rid)
        if color and ptype==0:
            f['palette']=self.cluts.get(rid)
            if f['palette'] is None:
                self.warn_once(cursor+58,2,'missing_bitmap_palette',rid,
                    f'indexed bitmap requires missing clut {rid}; showing an inverted grayscale index preview, which does not reproduce its original colors')
            else:
                indices=set()
                mask=(1<<bits)-1
                for y in range(sb-st):
                    for x in range(sr-sl):
                        pixel=sl-left+x;byte=self.data[pixels+(st-top+y)*row+(pixel*bits//8)]
                        indices.add((byte>>(8-bits-(pixel*bits%8)))&mask)
                absent=indices-f['palette'].keys()
                if absent:self.warn_once(cursor+58,2,'missing_bitmap_indices',rid,f'clut {rid} lacks {len(absent)} used indices; those indices use neutral fallback')
        return pixels+need
    def font_at_style(self,ident,offset):
        if ident in self.metric_cache:return self.metric_cache[ident]
        if not 0<=ident<len(self.font_styles):self.fail(f'0x{offset:x}: undefined Pro font style {ident}')
        style=dict(self.font_styles[ident]);size=style['size'];face=style['face']
        if not 0<size<=4096:self.fail('invalid Pro point size')
        style['color']=self.resolve_paint(style['state'] or 0xc006,style['color_ref'],style['offset']+18,color_offset=style['offset']+20)
        if not isinstance(style['color'],str):
            self.warn_once(style['offset'],22,'text_gradient',ident,'pattern/gradient glyph paint is not established; using its foreground or first gradient color')
            style['color']=(style['color']['gradient']['colors'][0] if 'gradient' in style['color'] else style['color']['foreground'])
        if face&~0xb7f or style['back'] or style['state'] not in (0,0xc005,0xc006):
            self.warn_once(style['offset'],22,'font_effect',ident,'font style has unresolved effect/tracking fields; ordinary glyphs retained')
        if face&0xb00:
            self.warn_once(style['offset'],22,'script_smallcaps',ident,'superscript, subscript or small-cap typography uses an explicit SVG fallback profile; original effect sizing is not established')
        m=self.fonts.resolve(style['font_id'],size,face&127)
        self.metric_cache[ident]=(style,m)
        return style,m

    def text_object(self,obj,cursor,end,reference,note):
        f=obj.fields
        if reference<8 or reference%4:self.fail('invalid Pro text handle')
        try:beg,stop=self.texts[(reference-8)//4]
        except KeyError:self.fail('missing Pro character block')
        n,nlines,nmods,state,extra=self.unpack('3I2H',cursor,end)
        original_cursor=cursor;cursor+=16
        if note:
            f['note_metadata']=self.unpack('20s',cursor,end)[0].hex();cursor+=20
            self.warn_once(obj.offset,34,'note_appearance',0,'note text retained; original note-window decoration is not reproduced')
        if nmods+1>(end-cursor)//4:self.fail('truncated Pro text modification table')
        mods=[self.unpack('2H',cursor+4*i,end) for i in range(nmods+1)];cursor+=4*(nmods+1)
        if any(a>b for (a,_),(b,_) in zip(mods,mods[1:])):self.fail('unordered Pro text modification table')
        if any(pos>n+1 for pos,sel in mods):self.fail('Pro text modification position exceeds character count')
        if not mods or mods[-1][1]!=65535:self.problem(original_cursor,end-original_cursor,'text_terminator','missing Pro text modification terminator',True)
        # Exact allocation extents distinguish a saved line table from an
        # absent cache. Never search for plausible line records in other data.
        remain=end-cursor
        if remain in (0,2):rows=[]
        elif remain in (26*(nlines+1),26*(nlines+1)+2):
            rows=[self.unpack('2H4iHi',cursor+26*i,end) for i in range(nlines+1)]
            cursor+=26*(nlines+1)
        else:self.fail('Pro text line-table extent disagrees with allocation size')
        chars=self.data[beg+8:min(stop,beg+8+n)]
        if len(chars)!=n:self.problem(beg,stop-beg,'text_length','Pro character allocation is shorter than declared text; surviving bytes retained',True)
        f.update(text_bytes=chars,text_modifications=mods,line_metrics=rows,text_state=(state,extra),text_fragments=[])
        original=f['box']
        if 'rotation' in f:
            lt,ll,lb,lr=f['rotation']['local_box'];t,l,_,_=original
            original=(t+lt,l+ll,t+lb,l+lr)
        top,left,bottom,right=original;f['text_box']=original
        fontmods=[(pos,sel) for pos,sel in mods if sel<32768]
        paramods=[(pos,sel&32767) for pos,sel in mods if 32768<=sel<65535]
        if not fontmods and chars:self.fail('Pro text has no font selection')
        fpositions=[p for p,v in fontmods];ppositions=[p for p,v in paramods]
        def font_at(at):
            idx=bisect_right(fpositions,at)-1
            if idx<0:self.fail('Pro text has no initial font selection')
            ident=fontmods[idx][1];style,m=self.font_at_style(ident,obj.offset)
            return ident,style,m
        default_para=dict(align=0,left=0,first=0,right=0,line=0,before=0,after=0,modes=(-1,0,0),tabs=[],reserved=0)
        def para_at(at):
            if not paramods:return default_para
            idx=bisect_right(ppositions,at)-1
            ident=paramods[max(0,idx)][1]
            if ident>=len(self.paragraphs):self.fail('undefined Pro paragraph style')
            return self.paragraphs[ident]
        def chunks(start,stop):
            at=start
            while at<stop:
                ident,style,m=font_at(at)
                j=bisect_right(fpositions,at)
                nxt=min(stop,fpositions[j] if j<len(fpositions) else stop)
                yield at,nxt,ident,style,m
                at=nxt
        def field_width(start,stop):
            return sum(m.width(chars[a:b]) for a,b,ident,style,m in chunks(start,stop))
        if rows and rows[-1][0]<len(chars):
            self.problem(original_cursor,end-original_cursor,'stale_text_cache',
                'saved line cache does not cover the current text; relaying out all surviving characters',True)
            f['discarded_line_cache']=True;rows=[]
        if rows:
            starts=[row[0] for row in rows]
            if not starts or starts[0]!=0 or starts!=sorted(starts) or starts[-1]>n+1:self.fail('invalid Pro saved line offsets')
            ranges=[(min(a,len(chars)),min(b,len(chars)),row) for a,b,row in zip(starts,starts[1:],rows)]
            if starts[-1]<len(chars):self.fail('Pro line offsets do not cover character data')
        else:
            self.warn_once(original_cursor,end-original_cursor,'uncached_text_layout',0,
                'saved text-line cache is absent; paragraphs are laid out from their styles and substituted bitmap metrics')
            # Word wrapping for an absent cache is explicitly a rendering
            # profile, not an inferred table or a recovered byte boundary.
            ranges=[];start=0
            while start<len(chars):
                para=para_at(start);first=start==0 or chars[start-1]==13
                available=max(1,right-left-para['left']+para['right']-(para['first'] if first else 0))
                at=start;width=0;word=None
                while at<len(chars):
                    c=chars[at]
                    if c==13:at+=1;break
                    ident,style,m=font_at(at)
                    advance=m.width(bytes((c,))) if c!=9 else 36-width%36
                    if width+advance>available and at>start:
                        if word is not None and word>start:at=word
                        break
                    width+=advance;at+=1
                    if c==32:word=at
                ranges.append((start,at,None));start=at
        y=top
        for start,stop,row in ranges:
            content_stop=stop
            while content_stop>start and chars[content_stop-1] in (0,13):content_stop-=1
            para=para_at(start);align=para['align']
            if align not in (-1,0,1,2):
                self.warn_once(obj.offset,34,'paragraph_alignment',align,f'undefined alignment {align}; left alignment');align=0
            first=start==0 or chars[start-1]==13
            origin=para['left']+(para['first'] if first else 0)
            parts=[];width=0
            # Split at tabs, then font changes; right/center/decimal stops use
            # the following tab-delimited field, including all of its styles.
            at=start
            while at<content_stop:
                if chars[at]==9:
                    following=chars.find(b'\t',at+1,content_stop)
                    if following<0:following=content_stop
                    stops=[tab for tab in para['tabs'] if tab['position']-origin>width]
                    tab=min(stops,key=lambda v:v['position']) if stops else None
                    if tab:
                        amount=0
                        if tab['align'] in (1,2):amount=field_width(at+1,following)/(2 if tab['align']==2 else 1)
                        elif tab['align']==3:
                            decimal=bytes((tab['decimal']&255,));decimal_at=chars.find(decimal,at+1,following)
                            amount=field_width(at+1,decimal_at if decimal_at>=0 else following)
                        elif tab['align']!=0:self.warn_once(obj.offset,34,'tab_alignment',tab['align'],'unknown tab alignment; left-tab fallback')
                        next_width=max(width,tab['position']-origin-amount)
                        if tab['leader'] not in (0,32):
                            ident,style,m=font_at(at);char=bytes((tab['leader']&255,));advance=m.width(char)
                            if advance>0:
                                number=min(10000,int((next_width-width)//advance))
                                if number:parts.append((width,char*number,ident,style,m))
                        width=next_width
                    else:
                        self.warn_once(obj.offset,34,'default_tabs',0,'text uses tabs beyond its explicit stops; fallback stops occur every 36 drawing units')
                        width=(math.floor((width+origin)/36)+1)*36-origin
                    at+=1;continue
                next_tab=chars.find(b'\t',at,content_stop)
                limit=content_stop if next_tab<0 else next_tab
                for a,b,ident,style,m in chunks(at,limit):
                    raw=chars[a:b];parts.append((width,raw,ident,style,m));width+=m.width(raw)
                at=limit
            height=max((m.ascent+m.descent+m.leading for _,_,_,_,m in parts),default=12)
            ascent=max((m.ascent for _,_,_,_,m in parts),default=9)
            if row:
                _,lineflags,saved_height,saved_ascent,dx,saved_width,line_state,dy=row
                height=saved_height/65536 or height;ascent=saved_ascent/65536 or ascent
                baseline=top+dy/65536+ascent;origin+=dx/65536
                if content_stop>start and abs(saved_width/65536-width)>1/65536:
                    self.warn_once(obj.offset,34,'text_advances',0,'saved text widths differ from the bitmap font advances; stored baselines and line breaks are retained, with bitmap spacing')
            else:
                if first:y+=para['before']*(height if para['modes'][1]==-1 else 1)
                baseline=y+ascent
            usable=max(0,right-left-origin+para['right'])
            x=left+origin+(usable-width)/2 if align==1 else right+para['right']-width if align==-1 else left+origin
            spaces=chars[start:content_stop].count(b' ')
            extra=max(0,usable-width)/spaces if align==2 and spaces and stop<len(chars) and chars[stop-1]!=13 else 0
            expanded=0
            for px,raw,ident,style,m in parts:
                sx=x+px+expanded
                pieces=[raw] if not (extra or style['face']&0x800) else [bytes((c,)) for c in raw]
                for piece in pieces:
                    used=m;display=piece;shift=0
                    if style['face']&0x800 and piece.decode('mac_roman').islower():
                        try:display=piece.decode('mac_roman').upper().encode('mac_roman')
                        except UnicodeError:display=piece
                        used=self.fonts.resolve(style['font_id'],style['size']*.8,style['face']&127)
                    if style['face']&0x100:shift-=style['size']/3
                    if style['face']&0x200:shift+=style['size']/3
                    f['text_fragments'].append(dict(font_id=style['font_id'],font_index=ident+1,face=style['face'],color=style['color'],
                        text_layout=mt.Layout(used,original,height,[(sx,baseline+shift,display)])))
                    advance=m.width(piece)+extra*piece.count(b' ')
                    sx+=advance;expanded+=extra*piece.count(b' ')
            if not row:
                spacing=height*(1+para['line']) if para['modes'][0]==-1 else max(height,para['line'])
                y+=max(1,spacing)
                if stop>start and chars[stop-1]==13:y+=para['after']*(height if para['modes'][2]==-1 else 1)
        return cursor


def rgb16(values):
    return '#'+''.join(f'{v>>8:02x}' for v in values)


def rgb_float(values):
    return '#'+''.join(f'{max(0,min(255,round(v*255))):02x}' for v in values)


def parse(data,api,*,fonts=None,recover=False,require_complete=False,resource_fork=None):
    return Decoder(api,data,fonts,recover,require_complete,resource_fork).parse()
def paint(renderer,value):
    if isinstance(value,str):return ii.paint(renderer,value)
    api=sys.modules[type(renderer).__module__];E=api.element;num=api.number
    import json
    key=json.dumps(value,sort_keys=True,separators=(',',':'))
    if not hasattr(renderer,'pro_paints'):renderer.pro_paints={}
    if key in renderer.pro_paints:return 'url(#'+renderer.pro_paints[key]+')'
    ident='pro-paint-'+str(len(renderer.pro_paints));renderer.pro_paints[key]=ident
    if 'pattern' in value:
        pat=E(renderer.defs,'pattern',id=ident,width=8,height=8,patternUnits='userSpaceOnUse')
        E(pat,'rect',width=8,height=8,fill='white')
        pts=[(x,y) for y,row in enumerate(bytes.fromhex(value['pattern'])) for x in range(8) if row&(128>>x)]
        E(pat,'path',d=mt.pixel_path(pts),fill=value['foreground'])
    else:
        grad=value['gradient'];colors=grad['colors'];kind=grad['kind']
        if kind in (1,2):colors=list(reversed(colors))
        positions=[i/max(1,len(colors)-1) for i in range(len(colors))]
        stops=list(zip(positions,colors))
        if kind==0:
            offset=max(0,min(1,grad['offset']))
            if offset==1:stops=list(zip(positions,reversed(colors)))
            elif offset:
                stops=[(offset*(1-t),color) for t,color in reversed(stops[1:])]+[(offset+(1-offset)*t,color) for t,color in stops]
            angle=math.radians(grad['angle']);dx=math.cos(angle)/2;dy=-math.sin(angle)/2
            element=E(renderer.defs,'linearGradient',id=ident,x1=num(.5-dx),y1=num(.5-dy),x2=num(.5+dx),y2=num(.5+dy))
        elif kind==1:
            t,l,b,r=grad['center'];cx=(l+r)/2;cy=(t+b)/2
            element=E(renderer.defs,'radialGradient',id=ident,cx=num(cx),cy=num(cy),r='0.5',fx=num(cx),fy=num(cy))
        else:
            t,l,b,r=grad['center'];cx=(l+r)/2;cy=(t+b)/2
            element=E(renderer.defs,'pattern',id=ident,width=1,height=1,patternContentUnits='objectBoundingBox')
            for i,(a,b,end) in enumerate((((0,0),(1,0),(cx,0)),((1,0),(1,1),(1,cy)),((1,1),(0,1),(cx,1)),((0,1),(0,0),(0,cy)))):
                gid=ident+'-'+str(i)
                linear=E(renderer.defs,'linearGradient',id=gid,gradientUnits='userSpaceOnUse',x1=num(cx),y1=num(cy),x2=num(end[0]),y2=num(end[1]))
                for pos,color in stops:E(linear,'stop',offset=num(pos),stop_color=color)
                # Adjacent wedges partition the paint tile. Antialiasing each
                # shared edge independently would leak the background through.
                E(element,'path',d=f'M{num(cx)} {num(cy)} L{a[0]} {a[1]} L{b[0]} {b[1]} Z',fill='url(#'+gid+')',shape_rendering='crispEdges')
        if kind!=2:
            for pos,color in stops:E(element,'stop',offset=num(pos),stop_color=color)
    return 'url(#'+ident+')'


def path_data(nodes,num):
    def anchor(node):return node[1][len(node[1])//2]
    def pair(point):return num(point[0])+' '+num(point[1])
    path=['M'+pair(anchor(nodes[0]))]
    for previous,node in zip(nodes,nodes[1:]):
        old=previous[1];new=node[1];point=anchor(node)
        if len(old)==3 or len(new)==3:
            outgoing=old[2] if len(old)==3 else anchor(previous)
            incoming=new[0] if len(new)==3 else point
            path.append('C'+pair(outgoing)+' '+pair(incoming)+' '+pair(point))
        else:path.append('L'+pair(point))
    if len(nodes)>1 and anchor(nodes[-1])==anchor(nodes[0]):path.append('Z')
    return ' '.join(path)


def png_bitmap(obj):
    f=obj.fields;st,sl,sb,sr=f['source_rect'];top,left,bottom,right=f['bitmap_bounds']
    width=sr-sl;height=sb-st;bits=f['pixel_bits'];stride=f['row_bytes'];raw=f['bitmap']
    palette=f.get('palette') or {};pixels=bytearray()
    for y in range(st-top,sb-top):
        pixels.append(0)
        for x in range(sl-left,sr-left):
            if f['pixel_type']==16:
                if bits==32:
                    at=y*stride+4*x;color=tuple(raw[at+1:at+4])
                else:
                    val=struct.unpack_from('>H',raw,y*stride+2*x)[0]
                    color=tuple(((val>>shift)&31)*255//31 for shift in (10,5,0))
            else:
                val=(raw[y*stride+(x*bits//8)]>>(8-bits-(x*bits%8)))&((1<<bits)-1)
                gray=255-round(val*255/((1<<bits)-1));color=palette.get(val,(gray,gray,gray))
            pixels.extend(color)
    def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',width,height,8,2,0,0,0))+
            chunk(b'IDAT',zlib.compress(pixels,9))+chunk(b'IEND',b''))


def render(renderer,parent,obj):
    api=sys.modules[type(renderer).__module__];E=api.element;num=api.number
    f=obj.fields;k=f['file_kind'];layer=f.get('layer')
    if layer and renderer.layer is not None and renderer.layer!=layer['index']:return
    g=E(parent,'g',data_source_offset=obj.offset,data_macdraw_pro_type=k)
    if layer:
        g.set('data-layer',ii.xml_text(layer['name']))
        if layer['flags']&0x8000 and renderer.layer is None:
            g.set('display','none');bounds=renderer.bounds;renderer.bounds=[]
            clone=api.Object(obj.offset,obj.kind,obj.attrs,dict(f),obj.children,obj.end,obj.count)
            clone.fields.pop('layer');render(renderer,g,clone);renderer.bounds=bounds
            return
    if k==10 and not f['flags']&64:
        for child in obj.children:render(renderer,g,child)
        return
    if k==11:return
    stroke=paint(renderer,f['stroke']);fill=paint(renderer,f['fill'])
    if k in (7,8,9):
        attrs=dict(stroke=stroke,fill=fill,stroke_width=num(f['width']),stroke_linejoin='round',stroke_linecap='square',fill_rule='evenodd')
        if f.get('dash'):attrs['stroke_dasharray']=' '.join(num(v) for v in f['dash'])
        E(g,'path',d=path_data(f['nodes'],num),**attrs)
        renderer.add_bounds(f['box'])
    elif k==12:
        t,l,b,r=f['box'];rotation=f.get('rotation');shape=f['box']
        if rotation:
            lt,ll,lb,lr=rotation['local_box'];shape=(t+lt,l+ll,t+lb,l+lr)
            g.set('transform',f'rotate({num(math.degrees(rotation["angle"]))} {num(l+(ll+lr)/2)} {num(t+(lt+lb)/2)})')
        tt,ll,bb,rr=shape
        if rr<=ll or bb<=tt:return
        renderer.add_bounds(f['box'])
        im=E(g,'image',x=num(ll),y=num(tt),width=num(rr-ll),height=num(bb-tt),preserveAspectRatio='none')
        im.set('{'+api.XLINK+'}href','data:image/png;base64,'+base64.b64encode(png_bitmap(obj)).decode('ascii'))
    else:
        fields=dict(f,stroke=stroke,fill=fill);fields.pop('layer',None)
        clone=api.Object(obj.offset,obj.kind,obj.attrs,fields,[],obj.end,obj.count)
        ii.render(renderer,g,clone)
