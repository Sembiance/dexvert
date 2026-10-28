/* Vibe coded by Codex */
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <io.h>
static void u16(unsigned char*b,int o,uint16_t v){memcpy(b+o,&v,2);}
static void u32(unsigned char*b,int o,uint32_t v){memcpy(b+o,&v,4);}
static uint32_t get(unsigned char*b,int o){uint32_t v;memcpy(&v,b+o,4);return v;}
int main(int argc,char**argv){
 _setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);
 if(argc!=3)return 10;
 HMODULE h[2]={LoadLibraryA(argv[1]),LoadLibraryA(argv[2])};
 short (__stdcall *dec[2])(void*);
 for(int i=0;i<2;i++){
  if(!h[i]){fprintf(stderr,"load %d error %lu\n",i,GetLastError());return 11;}
  dec[i]=(void*)GetProcAddress(h[i],"dcmpToolVoxDecompress");
  short (__stdcall *start)(void*)=(void*)GetProcAddress(h[i],"voxStartup");
  if(start){unsigned char p[48]={0};u16(p,0,48);if(start(p))return 12;}
 }
 
 setvbuf(stdin,NULL,_IONBF,0);setvbuf(stdout,NULL,_IONBF,0);
 uint32_t ready=0x31585756;fwrite(&ready,4,1,stdout);fflush(stdout);
 uint32_t req[3];
 while(fread(req,12,1,stdin)==1){
  
  if(req[0]>1||req[1]>67108864||req[2]>536870912)return 13;
  unsigned char *src=calloc(1,req[1]+4096),*dst=calloc(1,req[2]+4096);
  if(!src||!dst||!req[1]||fread(src,req[1],1,stdin)!=1)return 14;
  unsigned char p[142]={0};u16(p,0,req[0]?142:90);
  u32(p,8,0x10201);u32(p,12,(uint32_t)src);u32(p,16,req[1]);
  u32(p,0x1e,0x20200);u32(p,0x22,(uint32_t)dst);u32(p,0x26,req[2]);
  u32(p,0x3e,0x3f800000);u16(p,0x32,2);
  
  short ret=dec[req[0]](p);
  
  uint32_t ans[5]={(uint16_t)ret,get(p,0x4a),get(p,0x2a),get(p,0x2e),get(p,0x14)};
  if(ans[2]>req[2])return 15;
  fwrite(ans,20,1,stdout);fwrite(dst,ans[2],1,stdout);fflush(stdout);
  free(src);free(dst);
 }
 return 0;
}
