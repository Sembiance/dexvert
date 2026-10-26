/* Vibe coded by Codex
 * GDI rendering service. The SCM parser and all decompression live in Python.
 * Build: x86_64-w64-mingw32-gcc -O2 -s -o screenCamVideoRender.exe
 *        screenCamVideoRender.c -lgdi32 -luser32
 */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <io.h>
#include <fcntl.h>

static HDC dc, capture, source, saved;
static HBITMAP screenbmp, capturebmp, sourcebmp, savedbmp;
static uint32_t *screenbits, *capturebits, *previous;
static RGBQUAD palette[256];
static int palette_count=256, width, height, cursor_x, cursor_y;
static int hot_x,hot_y,cursor_w,cursor_h,cursor_visible;
static int cursor_trim_x,cursor_trim_y;
static uint32_t cursor_and[1024],cursor_xor[1024];
static HBRUSH brushes[12];
static HRGN region, clip;
static HFONT font;
static HBRUSH current_brush;
static HPEN current_pen;
static BITMAPINFO *dib;
static uint8_t *dib_bits;
static int dib_monochrome;
static int dib_size;
static uint8_t *work;

static void die(const char *msg) { fprintf(stderr,"ScreenCam renderer: %s\n",msg); exit(2); }
static void readall(void *p,size_t n) { if(n && fread(p,1,n,stdin)!=n) die("truncated protocol"); }
static void writeall(void *p,size_t n) { if(n && fwrite(p,1,n,stdout)!=n) exit(3); }
static DWORD rop(int n) { return ((DWORD)n&255)<<16; }
typedef struct { int mode; POINT window_org,viewport_org; SIZE window_ext,viewport_ext; } MapState;
static MapState device_coordinates(void) {
    MapState m;m.mode=GetMapMode(dc);
    GetWindowOrgEx(dc,&m.window_org);GetViewportOrgEx(dc,&m.viewport_org);
    GetWindowExtEx(dc,&m.window_ext);GetViewportExtEx(dc,&m.viewport_ext);
    if(m.mode!=MM_TEXT)SetMapMode(dc,MM_TEXT);
    SetWindowOrgEx(dc,0,0,NULL);SetViewportOrgEx(dc,0,0,NULL);return m;
}
static void restore_coordinates(MapState m) {
    /* Preserve the original call order, including MM_ISOTROPIC rounding. */
    if(m.mode!=MM_TEXT)SetMapMode(dc,m.mode);
    SetWindowOrgEx(dc,m.window_org.x,m.window_org.y,NULL);
    if(m.mode!=MM_TEXT)SetWindowExtEx(dc,m.window_ext.cx,m.window_ext.cy,NULL);
    SetViewportOrgEx(dc,m.viewport_org.x,m.viewport_org.y,NULL);
    if(m.mode!=MM_TEXT)SetViewportExtEx(dc,m.viewport_ext.cx,m.viewport_ext.cy,NULL);
}
static COLORREF color(uint32_t v) {
    if(v&0x01000000) { RGBQUAD c=palette[v&255]; return RGB(c.rgbRed,c.rgbGreen,c.rgbBlue); }
    return v&0xffffff;
}
static void select_brush(HBRUSH b,int owned) {
    SelectObject(dc,b); if(current_brush) DeleteObject(current_brush); current_brush=owned?b:NULL;
}
static void select_pen(HPEN p,int owned) {
    SelectObject(dc,p); if(current_pen) DeleteObject(current_pen); current_pen=owned?p:NULL;
}
static HBITMAP make_dib(HDC target,int w,int h,uint32_t **bits) {
    BITMAPINFO b; memset(&b,0,sizeof(b)); b.bmiHeader.biSize=40;
    b.bmiHeader.biWidth=w; b.bmiHeader.biHeight=-h; b.bmiHeader.biPlanes=1;
    b.bmiHeader.biBitCount=32; HBITMAP bm=CreateDIBSection(target,&b,DIB_RGB_COLORS,(void **)bits,NULL,0);
    if(!bm) die("CreateDIBSection failed"); SelectObject(target,bm); return bm;
}
static void init(int w,int h) {
    if(w<=0||h<=0||w>16384||h>16384) die("invalid dimensions");
    if(dc) { DeleteDC(dc);DeleteDC(capture);DeleteDC(source);DeleteDC(saved);
        DeleteObject(screenbmp);DeleteObject(capturebmp); if(sourcebmp)DeleteObject(sourcebmp);
        if(savedbmp)DeleteObject(savedbmp); }
    for(int i=0;i<12;i++){ if(brushes[i])DeleteObject(brushes[i]);brushes[i]=NULL; }
    if(font)DeleteObject(font);font=NULL;
    if(current_brush)DeleteObject(current_brush);current_brush=NULL;
    if(current_pen)DeleteObject(current_pen);current_pen=NULL;
    if(region)DeleteObject(region);if(clip)DeleteObject(clip);
    region=CreateRectRgn(0,0,0,0);clip=CreateRectRgn(0,0,w,h);
    width=w;height=h;dc=CreateCompatibleDC(NULL);capture=CreateCompatibleDC(NULL);
    source=CreateCompatibleDC(NULL);saved=CreateCompatibleDC(NULL);sourcebmp=savedbmp=NULL;
    screenbmp=make_dib(dc,w,h,&screenbits);capturebmp=make_dib(capture,w,h,&capturebits);
    free(previous);previous=calloc((size_t)w*h,4);free(work);work=malloc((size_t)w*h*4+((w+15)/16)*((h+15)/16)*2+16);
    if(!previous||!work)die("out of memory");
    PatBlt(dc,0,0,w,h,WHITENESS);
    SetBkColor(dc,RGB(255,255,255));SetTextColor(dc,0);SetBkMode(dc,OPAQUE);
    cursor_visible=cursor_x=cursor_y=hot_x=hot_y=cursor_trim_x=cursor_trim_y=0;cursor_w=cursor_h=32;
    for(int i=0;i<1024;i++){cursor_and[i]=0xffffff;cursor_xor[i]=0;}
    HDC desk=GetDC(NULL);PALETTEENTRY pe[256];memset(pe,0,sizeof(pe));
    GetSystemPaletteEntries(desk,0,256,pe);ReleaseDC(NULL,desk);
    for(int i=0;i<256;i++)palette[i]=(RGBQUAD){pe[i].peBlue,pe[i].peGreen,pe[i].peRed,0};
    palette_count=256;
}
static void source_bitmap(void) {
    if(!dib)die("bitmap used before definition");
    HBITMAP bm;
    if(dib_monochrome) bm=CreateBitmap(dib->bmiHeader.biWidth,abs(dib->bmiHeader.biHeight),1,1,NULL);
    else bm=CreateCompatibleBitmap(dc,dib->bmiHeader.biWidth,abs(dib->bmiHeader.biHeight));
    if(!bm)die("source bitmap allocation failed");
    SelectObject(source,bm); if(sourcebmp)DeleteObject(sourcebmp);sourcebmp=bm;
    SetDIBits(source,bm,0,abs(dib->bmiHeader.biHeight),dib_bits,dib,DIB_RGB_COLORS);
}
static void set_dib(int *a,uint8_t *p,size_t n) {
    int w=a[0],h=a[1],depth=a[2],compression=a[3],indexed=a[4],count=a[5],op=a[6],cbytes=a[7];
    if(count>256||count<0||w<1||h<1||w>32768||h>32768||cbytes<0||(size_t)cbytes>n)die("invalid DIB");
    free(dib);dib=calloc(1,40+1024); if(!dib)die("out of memory");
    BITMAPINFOHEADER *b=&dib->bmiHeader;b->biSize=40;b->biWidth=w;b->biHeight=h;
    b->biPlanes=1;b->biBitCount=depth;b->biCompression=compression;b->biSizeImage=n-cbytes;
    b->biClrUsed=depth==1?0:count;
    dib_monochrome=depth==1&&count==0;
    if(indexed) {
        if(count) { for(int i=0;i<count;i++)dib->bmiColors[i]=palette[p[i]]; }
        else if(op==0x45||palette_count==2) { dib->bmiColors[0]=palette[0];dib->bmiColors[1]=palette[palette_count-1]; }
        else {
            COLORREF c=GetTextColor(dc),d=GetBkColor(dc);
            dib->bmiColors[0]=(RGBQUAD){GetBValue(c),GetGValue(c),GetRValue(c),0};
            dib->bmiColors[1]=(RGBQUAD){GetBValue(d),GetGValue(d),GetRValue(d),0};
        }
    } else if(compression==3)memcpy(dib->bmiColors,p,12);
    else if(count)memcpy(dib->bmiColors,p,count*4);
    else if(op==0x45) {dib->bmiColors[0]=(RGBQUAD){0,0,0,0};dib->bmiColors[1]=(RGBQUAD){255,255,255,0};}
    else {
        COLORREF c=GetTextColor(dc),d=GetBkColor(dc);
        dib->bmiColors[0]=(RGBQUAD){GetBValue(c),GetGValue(c),GetRValue(c),0};
        dib->bmiColors[1]=(RGBQUAD){GetBValue(d),GetGValue(d),GetRValue(d),0};
    }
    free(dib_bits);dib_size=n-cbytes;dib_bits=malloc(dib_size+1);if(!dib_bits)die("out of memory");memcpy(dib_bits,p+cbytes,dib_size);
}
static void set_cursor(int op,int *a,uint8_t *p,size_t n) {
    if(cursor_visible) {MapState m=device_coordinates();restore_coordinates(m);}
    int stride=a[4],w=a[2],h=a[3];
    if(w<1||w>32||h<1||h>32||stride<1||stride>128)die("invalid cursor dimensions");
    size_t masksize=(size_t)stride*h,need=op==56?masksize*2:masksize+(size_t)w*h;
    if(n<need)die("truncated cursor bitmap");
    /* Shape changes preserve the original player's cropped cursor origin. */
    cursor_x+=hot_x-a[0];cursor_y+=hot_y-a[1];
    hot_x=a[0];hot_y=a[1];cursor_w=w;cursor_h=h;cursor_visible=1;
    for(int y=0;y<h;y++)for(int x=0;x<w;x++) {
        int i=y*32+x;cursor_and[i]=(p[y*stride+x/8]&(128>>(x&7)))?0xffffff:0;
        if(op==56)cursor_xor[i]=(p[masksize+y*stride+x/8]&(128>>(x&7)))?0xffffff:0;
        else {RGBQUAD c=palette[p[masksize+y*w+x]];cursor_xor[i]=(c.rgbRed<<16)|(c.rgbGreen<<8)|c.rgbBlue;}
    }
    cursor_trim_x=cursor_trim_y=0;
    if(op==56) {
        cursor_trim_y=h;
        for(int y=0;y<h;y++)for(int x=0;x<w;x++) {
            int i=y*32+x;
            if(cursor_and[i]!=0xffffff||cursor_xor[i]) {
                if(y<cursor_trim_y)cursor_trim_y=y;
            }
        }
    }
    {MapState m=device_coordinates();restore_coordinates(m);}
}
static void capture_frame(int key) {
    GdiFlush();memcpy(capturebits,screenbits,(size_t)width*height*4);
    if(cursor_visible)for(int y=0;y<cursor_h;y++)for(int x=0;x<cursor_w;x++) {
        int dx=cursor_x-cursor_trim_x+x,dy=cursor_y-cursor_trim_y+y;
        if(dx>=0&&dx<width&&dy>=0&&dy<height) {int i=y*32+x;capturebits[dy*width+dx]=(capturebits[dy*width+dx]&cursor_and[i])^cursor_xor[i];}
    }
    uint32_t size=0;
    if(key) { size=(uint32_t)width*height*4;writeall(&size,4);writeall(capturebits,size); }
    else {
        int cols=(width+15)/16,rows=(height+15)/16,vectors=(cols*rows*2+3)&~3,idx=0;
        memset(work,0,vectors);size=vectors;int changed=0;
        for(int y=0;y<height;y+=16)for(int x=0;x<width;x+=16,idx++) {
            int bw=width-x<16?width-x:16,bh=height-y<16?height-y:16,diff=0;
            for(int j=0;j<bh&&!diff;j++)diff=memcmp(capturebits+(y+j)*width+x,previous+(y+j)*width+x,bw*4);
            if(diff) {changed=1;work[idx*2]=1;
                for(int j=0;j<bh;j++)for(int i=0;i<bw;i++) {
                    uint32_t d=capturebits[(y+j)*width+x+i]^previous[(y+j)*width+x+i];memcpy(work+size,&d,4);size+=4;
                }
            }
        }
        if(!changed)size=0;writeall(&size,4);writeall(work,size);
    }
    memcpy(previous,capturebits,(size_t)width*height*4);fflush(stdout);
}

static void command(uint32_t op,int *a,int argc,uint8_t *p,size_t n) {
    switch(op) {
    case 0x100:set_dib(a,p,n);break;
    case 0x101:init(a[0],a[1]);break;
    case 0x102:capture_frame(a[0]);break;
    case 0:source_bitmap(); {MapState m=device_coordinates();
        BitBlt(dc,a[0],a[1],dib->bmiHeader.biWidth,dib->bmiHeader.biHeight,source,0,0,rop(a[2]));restore_coordinates(m);}break;
    case 1: {MapState m=device_coordinates();
        StretchDIBits(dc,a[0],a[1],dib->bmiHeader.biWidth,dib->bmiHeader.biHeight,0,0,dib->bmiHeader.biWidth,dib->bmiHeader.biHeight,dib_bits,dib,DIB_RGB_COLORS,SRCCOPY);restore_coordinates(m);}break;
    case 2:BitBlt(dc,a[0],a[1],a[2],a[3],dc,a[4],a[5],rop(a[6]));break;
    case 3:case 4:PatBlt(dc,a[0],a[1],a[2],a[3],rop(a[4]));break;
    case 5:source_bitmap();StretchBlt(dc,a[0],a[1],a[2],a[3],source,a[4],a[5],a[6],a[7],rop(a[8]));break;
    case 6:StretchBlt(dc,a[0],a[1],a[2],a[3],dc,a[4],a[5],a[6],a[7],rop(a[8]));break;
    case 7:StretchDIBits(dc,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],dib_bits,dib,DIB_RGB_COLORS,rop(a[8]));break;
    case 8: {POINT pt[2]={{0,0},{a[2],a[3]}};DPtoLP(dc,pt,2);StretchDIBits(dc,a[0],a[1],pt[1].x-pt[0].x,pt[1].y-pt[0].y,a[4],a[5],a[2],a[3],dib_bits,dib,DIB_RGB_COLORS,SRCCOPY);}break;
    case 9:TextOutA(dc,a[0],a[1],(char*)p,a[2]);break;
    case 10:ExtTextOutA(dc,a[0],a[1],a[2]&6,(a[2]&128)?(RECT*)(a+3):NULL,(char*)p,a[7],(a[2]&64)?a+8:NULL);break;
    case 11:Arc(dc,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7]);break;
    case 12:Chord(dc,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7]);break;
    case 13:Ellipse(dc,a[0],a[1],a[2],a[3]);break;
    case 14:Pie(dc,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7]);break;
    case 15:LineTo(dc,a[0],a[1]);break;
    case 16:MoveToEx(dc,a[0],a[1],NULL);LineTo(dc,a[2],a[3]);break;
    case 17:SetPixel(dc,a[0],a[1],color(a[2]));break;
    case 18:Polygon(dc,(POINT*)(a+2),a[1]);break;
    case 19:Polyline(dc,(POINT*)(a+2),a[1]);break;
    case 20:Rectangle(dc,a[0],a[1],a[2],a[3]);break;
    case 21:RoundRect(dc,a[0],a[1],a[2],a[3],a[4],a[5]);break;
    case 22:FloodFill(dc,a[0],a[1],color(a[2]));break;
    case 23:ExtFloodFill(dc,a[0],a[1],color(a[2]),a[3]);break;
    case 24:SetBkColor(dc,color(a[0]));break;
    case 25:SetTextColor(dc,color(a[0]));break;
    case 26:SetBkMode(dc,a[0]);break;
    case 27:SetROP2(dc,a[0]);break;
    case 28:SetPolyFillMode(dc,a[0]);break;
    case 29:SetStretchBltMode(dc,a[0]);break;
    case 30:SetMapMode(dc,a[0]>1&&a[0]<7?8:a[0]);break;
    case 31:SetBrushOrgEx(dc,a[0],a[1],NULL);break;
    case 32:SetViewportOrgEx(dc,a[0],a[1],NULL);break;
    case 33:SetViewportExtEx(dc,a[0],a[1],NULL);break;
    case 34:SetWindowOrgEx(dc,a[0],a[1],NULL);break;
    case 35:SetWindowExtEx(dc,a[0],a[1],NULL);break;
    case 36:case 37: {LOGPEN pen={a[0],{a[1],a[2]},color(a[3])};select_pen(CreatePenIndirect(&pen),1);}break;
    case 38:select_pen(GetStockObject(NULL_PEN),0);break;
    case 39:select_pen(GetStockObject((a[0]&1)?WHITE_PEN:BLACK_PEN),0);break;
    case 40:case 43: {LOGBRUSH b={a[0],color(a[1]),a[2]};select_brush(CreateBrushIndirect(&b),1);}break;
    case 41:case 42:case 44: {
        HBRUSH brush;
        if(op==44) {size_t sz=40+(dib->bmiHeader.biCompression==3?12:(dib->bmiHeader.biBitCount<=8?(dib->bmiHeader.biClrUsed?dib->bmiHeader.biClrUsed:1<<dib->bmiHeader.biBitCount)*4:0));
            uint8_t *tmp=malloc(sz+dib_size);memcpy(tmp,dib,sz);memcpy(tmp+sz,dib_bits,dib_size);brush=CreateDIBPatternBrushPt(tmp,DIB_RGB_COLORS);free(tmp);
        } else {source_bitmap();brush=CreatePatternBrush(sourcebmp);}
        if(op==42) {if(a[0]>=12)die("brush slot outside table");select_brush(brush,0);if(brushes[a[0]])DeleteObject(brushes[a[0]]);brushes[a[0]]=brush;}
        else select_brush(brush,1);
    }break;
    case 45:select_brush(GetStockObject(NULL_BRUSH),0);break;
    case 46:if(a[0]&128)select_brush(GetStockObject((a[0]&1)?WHITE_BRUSH:BLACK_BRUSH),0);
        else {if(a[0]>=12||!brushes[a[0]])die("undefined brush cache slot");select_brush(brushes[a[0]],0);}break;
    case 47: {LOGFONTA lf;memset(&lf,0,sizeof(lf));lf.lfHeight=a[0];lf.lfWidth=a[1];lf.lfEscapement=a[2];lf.lfOrientation=a[3];lf.lfWeight=a[4];
        memcpy(&lf.lfItalic,p,8);memcpy(lf.lfFaceName,p+8,a[5]<31?a[5]:31);
        HFONT f=CreateFontIndirectA(&lf);SelectObject(dc,f);if(font)DeleteObject(font);font=f;}break;
    case 48:SetTextCharacterExtra(dc,a[0]);break;
    case 49:SetTextJustification(dc,a[1],a[0]);break;
    case 50:SetTextAlign(dc,a[0]);break;
    case 51:for(int i=a[0];i<=a[1];i++)memcpy(&palette[i],p+(i-a[0])*4,4);palette_count=a[1]+1;break;
    case 52:SetRectRgn(clip,a[0],a[1],a[2],a[3]);SelectClipRgn(dc,clip);break;
    case 53: {HBRUSH b=SelectObject(dc,GetStockObject(NULL_BRUSH));FrameRgn(dc,region,b,a[0],a[1]);SelectObject(dc,b);}break;
    case 54:InvertRgn(dc,region);break;
    case 55:PaintRgn(dc,region);break;
    case 56:case 74:set_cursor(op,a,p,n);break;
    case 57: {MapState m=device_coordinates();cursor_visible=0;restore_coordinates(m);}break;
    case 58:cursor_x=a[0]-hot_x+cursor_trim_x;cursor_y=a[1]-hot_y+cursor_trim_y;
        if(cursor_visible){MapState m=device_coordinates();restore_coordinates(m);}break;
    case 59:break;
    case 61: {if(a[0]==2) {if(savedbmp){DeleteDC(saved);DeleteObject(savedbmp);savedbmp=NULL;saved=CreateCompatibleDC(NULL);}break;}
        MapState m=device_coordinates();HRGN oldclip=CreateRectRgn(0,0,0,0);int hasclip=GetClipRgn(dc,oldclip);
        if(a[0]==1)SelectClipRgn(dc,NULL);
        if(a[0]==0) {HBITMAP b=CreateCompatibleBitmap(dc,a[3]-a[1],a[4]-a[2]);SelectObject(saved,b);if(savedbmp)DeleteObject(savedbmp);savedbmp=b;BitBlt(saved,0,0,a[3]-a[1],a[4]-a[2],dc,a[1],a[2],SRCCOPY);}
        else if(a[0]==1&&savedbmp)BitBlt(dc,a[1],a[2],a[3]-a[1],a[4]-a[2],saved,0,0,SRCCOPY);
        if(a[0]!=0&&savedbmp) {DeleteDC(saved);DeleteObject(savedbmp);savedbmp=NULL;saved=CreateCompatibleDC(NULL);}
        restore_coordinates(m);if(a[0]==1)SelectClipRgn(dc,hasclip==1?oldclip:NULL);DeleteObject(oldclip);}break;
    case 65:break; /* MessageBeep is a system notification, not stored sound. */
    case 71:case 72: {HRGN dest=op==71?region:clip;SetRectRgn(dest,0,0,0,0);
        for(int i=0;i<a[0];i++){int *q=a+1+i*4;HRGN r=CreateRectRgn(q[0],q[1],q[2],q[3]);CombineRgn(dest,dest,r,RGN_OR);DeleteObject(r);}
        if(op==72)SelectClipRgn(dc,clip);}break;
    case 73:PolyPolygon(dc,(POINT*)(a+1+a[0]),a+1,a[0]);break;
    default:die("unsupported normalized command");
    }
}
int main(void) {
    _setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
    uint32_t h[3];uint8_t *buf=NULL;size_t capacity=0;
    while(fread(h,4,3,stdin)==3) {
        if(h[0]>268435456||h[2]>h[0]/4)die("invalid protocol length");
        if(h[0]>capacity){capacity=h[0]+16;buf=realloc(buf,capacity);if(!buf)die("out of memory");}
        readall(buf,h[0]);command(h[1],(int*)buf,h[2],buf+h[2]*4,h[0]-h[2]*4);
    }
    free(buf);return 0;
}
