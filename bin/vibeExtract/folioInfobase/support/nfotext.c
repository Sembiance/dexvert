/* Vibe coded by Claude
 *
 * nfotext.c -- headless Folio .NFO -> plain text + embedded-object extractor.
 *
 * Drives the real 32-bit Folio Views 4.2 Infobase engine (nfomgr4.dll) under
 * wine, CLI-only (no window).  The call sequence and the FIF read-callback
 * contract below were reverse-engineered from Folio's own console tool
 * NfoFind.exe, which is the ground-truth caller of this API:
 *
 *   Nfo_Initialize(lcid)
 *   Nfo_CreateSession(&session)
 *   Nfo_OpenInfobaseA(session, nfoPath, &openOpts, &infobase)
 *   Nfo_CreateBinderA(infobase, "", 1, out4, &binder, &out6)
 *   Nfo_GetCount(binder, &count)
 *   Nfo_ReadPageRecordsA(binder, 0, count, callback, ctx)
 *       callback(ctx, elementType, char* text, int len):
 *           elementType == 6            -> text run  (len bytes of body text)
 *           elementType in {0,8,9,0xd}  -> structural break (newline)
 *   Nfo_DestroyBinder / Nfo_CloseInfobase / Nfo_DestroySession / Nfo_Terminate
 *
 * openOpts is a 0x410-byte struct: [0]=0x410 (size), [8]=1, [0xc]=1.
 *
 * ---------------------------------------------------------------------------
 * EMBEDDED-OBJECT (image) EXTRACTION  --  `nfotext <in.nfo> <out.txt> <objdir>`
 * ---------------------------------------------------------------------------
 * Every Folio "embedded object" (imported graphic / OLE blob) lives in the
 * infobase Object table under the class name "Folio Objects".  The extraction
 * call sequence was recovered by disassembling the ground-truth caller
 * NFOFLT4.dll -- the .NFO export filter, the only module that imports the
 * object API (Nfo_CreateObjectIteratorA, Nfo_FirstA/NextA, Nfo_GetObjectIDA,
 * Nfo_OpenObject, Nfo_GetObjectSize, Nfo_ReadObject, Nfo_CloseObject,
 * Nfo_GetObjectClassA/NameA, Nfo_DestroyIterator).  Its inner loop (VA
 * 0x1000_1063e "Folio Objects" enumerator + the OpenObject/ReadObject/Close
 * primitive at 0x1001_2a21) is exactly:
 *
 *   Nfo_CreateObjectIteratorA(infobase, "Folio Objects", iterOpts, &iter)
 *        iterOpts -> {DWORD 0x2a; 0; ...}  (NFOFLT4's static 0x1002_91e0 blob)
 *   Nfo_FirstA(iter, 0, &objInfo)          objInfo[0]  = object name string
 *   loop:
 *     Nfo_GetObjectIDA(infobase, "Folio Objects", &objInfo, &objID)
 *     Nfo_GetObjectClassA(infobase, &objID, classBuf)   (3 args)
 *     Nfo_GetObjectNameA (infobase, &objID, nameBuf)    (3 args)
 *     Nfo_OpenObject(infobase, &objID, 4, &handle)      (mode 4 = read)
 *     Nfo_GetObjectSize(handle, &size)
 *     Nfo_ReadObject(handle, buf, len, &bytesRead)      (sequential cursor)
 *     Nfo_CloseObject(handle)
 *     Nfo_NextA(iter, 0, &objInfo)
 *   Nfo_DestroyIterator(iter)
 *
 * All argument counts are read from each export's stdcall `ret N`; all handles
 * (infobase/session) come from the text-path open sequence above.
 *
 * Objects are written to <objdir>/ EXACTLY AS STORED -- the raw bytes the
 * engine returns, with NO format conversion.  The engine reassembles objects
 * that are fragmented / page-split on disk, so this is more faithful than
 * carving.  A file's extension is chosen from the stored MAGIC bytes (BM->bmp,
 * GIF8->gif, D7CDC69A/01000900->wmf, " EMF"@40->emf, D0CF11E0->ole, %PDF->pdf,
 * FFD8FF->jpg, 89PNG->png, II*./MM.*->tif, else .bin).  Objects Folio keeps as
 * a raw DIB (a 2-byte type word + BITMAPINFOHEADER, no BITMAPFILEHEADER) match
 * no standalone magic and are written verbatim as .bin -- prepending a file
 * header would be a conversion, which is explicitly not done.
 *
 * NOTE on inline pictures: some infobases (e.g. p1/browsaim, p5/MAINMENU) hold
 * no Object-table objects at all -- their graphics are inline, Folio-compressed
 * record content that only the GUI display filters (FcBmp4/FcWmf4/FcPict4)
 * materialise while rendering; they are not enumerable through the headless
 * object/field API (Nfo_CreateFieldIteratorA returns end-of-data across the
 * whole corpus) and are not byte-carvable (compressed).  Such infobases yield
 * 0 objects here, by design.
 *
 * Everything is resolved dynamically via GetProcAddress so the DLL contract is
 * explicit and the tool degrades gracefully if the engine is missing.
 */
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <io.h>
#include <fcntl.h>

typedef int (WINAPI *initFn)(DWORD lcid);
typedef int (WINAPI *createSessionFn)(void* pSession);
typedef int (WINAPI *openFn)(void* session, const char* path, void* opts, void* pInfobase);
typedef int (WINAPI *createBinderFn)(void* infobase, const char* name, int flag,
                                     void* out4, void* out5, void* out6);
typedef int (WINAPI *getCountFn)(void* binder, void* pCountInfo);
typedef int (WINAPI *readRecFn)(void* binder, int start, int count, void* cb, void* ctx);
typedef int (WINAPI *closeInfFn)(void* infobase);
typedef int (WINAPI *destroyBinderFn)(void* binder);
typedef int (WINAPI *destroySessionFn)(void* session);
typedef int (WINAPI *termFn)(void);
typedef char* (WINAPI *getErrFn)(void);

/* --- embedded-object (Object-table) API; arg counts from each export's ret N,
 *     call sequence from NFOFLT4.dll (see file header). --- */
typedef int (WINAPI *createObjIterFn)(void* infobase, const char* cls, void* opts, void** ppIter);
typedef int (WINAPI *iterStepFn)(void* iter, int zero, void* objInfo);       /* First/Next: ret 0xc */
typedef int (WINAPI *destroyIterFn)(void* iter);                             /* ret 4 */
typedef int (WINAPI *getObjIDFn)(void* infobase, const char* cls, void* objInfo, void* objID);
typedef int (WINAPI *getObjStrFn)(void* infobase, void* objID, char* out);   /* Class/Name: ret 0xc */
typedef int (WINAPI *openObjFn)(void* infobase, void* objID, int mode, void** ppHandle);
typedef int (WINAPI *getObjSizeFn)(void* handle, DWORD* pSize);              /* ret 8 */
typedef int (WINAPI *readObjFn)(void* handle, void* buf, int len, DWORD* pRead);
typedef int (WINAPI *closeObjFn)(void* handle);                             /* ret 4 */

static FILE* g_out;
static unsigned long long g_bytes = 0;
static unsigned long g_text_runs = 0;
static unsigned long g_breaks = 0;
static volatile LONG g_done = 0;  /* set once all text is written + flushed */

/* Last-chance handler.  The Folio local-server COM teardown faults on process
 * exit under wine; by the time that happens the text is already flushed, so we
 * terminate cleanly (exit 0) instead of letting winedbg attach.  A fault that
 * occurs *before* extraction completes still exits non-zero. */
static LONG WINAPI topFilter(EXCEPTION_POINTERS* ep)
{
    if (g_out) fflush(g_out);
    fprintf(stderr, "(caught exception 0x%08lx; done=%ld)\n",
            ep->ExceptionRecord->ExceptionCode, g_done);
    ExitProcess(g_done ? 0 : 9);
    return EXCEPTION_EXECUTE_HANDLER; /* not reached */
}

/* FIF read callback. Matches NfoFind's 0x402d1b: stdcall, 4 args (ret 0x10). */
static int WINAPI fifCallback(void* ctx, int type, char* text, int len)
{
    (void)ctx;
    if (type == 6) {
        if (text && len > 0) {
            fwrite(text, 1, (size_t)len, g_out);
            g_bytes += (unsigned long long)len;
            g_text_runs++;
        }
    } else if (type == 0 || type == 8 || type == 9 || type == 0x0d) {
        fputc('\n', g_out);
        g_breaks++;
    }
    return 1; /* nonzero = continue */
}

#define GETPROC(var, type, name) \
    var = (type)GetProcAddress(h, name); \
    if (!var) { fprintf(stderr, "MISSING export %s\n", name); return 3; }

/* ------------------------- object extraction --------------------------- */

/* Extension from the stored MAGIC bytes -- objects are dumped exactly as
 * stored, so the extension only labels what the raw bytes already are. */
static const char* magic_ext(const unsigned char* b, size_t n)
{
    if (n >= 44 && b[40]==0x20 && b[41]=='E' && b[42]=='M' && b[43]=='F') return "emf";
    if (n >= 2  && b[0]=='B'  && b[1]=='M')                               return "bmp";
    if (n >= 4  && b[0]=='G'  && b[1]=='I'  && b[2]=='F' && b[3]=='8')    return "gif";
    if (n >= 4  && b[0]==0xD7 && b[1]==0xCD && b[2]==0xC6 && b[3]==0x9A)  return "wmf";
    if (n >= 4  && b[0]==0x01 && b[1]==0x00 && b[2]==0x09 && b[3]==0x00)  return "wmf";
    if (n >= 4  && b[0]==0xD0 && b[1]==0xCF && b[2]==0x11 && b[3]==0xE0)  return "ole";
    if (n >= 4  && b[0]=='%'  && b[1]=='P'  && b[2]=='D' && b[3]=='F')    return "pdf";
    if (n >= 3  && b[0]==0xFF && b[1]==0xD8 && b[2]==0xFF)                return "jpg";
    if (n >= 4  && b[0]==0x89 && b[1]=='P'  && b[2]=='N' && b[3]=='G')    return "png";
    if (n >= 4  && b[0]=='I'  && b[1]=='I'  && b[2]==0x2A && b[3]==0x00)  return "tif";
    if (n >= 4  && b[0]=='M'  && b[1]=='M'  && b[2]==0x00 && b[3]==0x2A)  return "tif";
    return "bin";
}

/* Sanitise a Folio object name/class into a safe leaf filename. */
static void sanitize(const char* in, char* out, size_t outsz)
{
    size_t j = 0;
    for (size_t i = 0; in[i] && j + 1 < outsz; i++) {
        unsigned char c = (unsigned char)in[i];
        if (c < 0x20 || c=='/' || c=='\\' || c==':' || c=='*' || c=='?' ||
            c=='"' || c=='<' || c=='>' || c=='|')
            out[j++] = '_';
        else
            out[j++] = (char)c;
    }
    if (j == 0) out[j++] = '_';
    out[j] = 0;
}

/* case-insensitive "does name end with .ext" */
static int ends_with_ext(const char* name, const char* ext)
{
    size_t ln = strlen(name), le = strlen(ext);
    if (ln < le + 1 || name[ln - le - 1] != '.') return 0;
    for (size_t i = 0; i < le; i++)
        if (tolower((unsigned char)name[ln - le + i]) != (unsigned char)ext[i]) return 0;
    return 1;
}

/* Iterate every "Folio Objects" object and dump its raw bytes to objdir/.
 * Returns object count; *pTotal gets the total bytes written. Best-effort:
 * a single object that fails is skipped, not fatal. */
static unsigned long extract_objects(HMODULE h, void* infobase, const char* objdir,
                                     getErrFn Nfo_GetErrorA, unsigned long long* pTotal)
{
    createObjIterFn Nfo_CreateObjectIteratorA =
        (createObjIterFn)GetProcAddress(h, "Nfo_CreateObjectIteratorA");
    iterStepFn    Nfo_FirstA           = (iterStepFn)GetProcAddress(h, "Nfo_FirstA");
    iterStepFn    Nfo_NextA            = (iterStepFn)GetProcAddress(h, "Nfo_NextA");
    destroyIterFn Nfo_DestroyIterator  = (destroyIterFn)GetProcAddress(h, "Nfo_DestroyIterator");
    getObjIDFn    Nfo_GetObjectIDA     = (getObjIDFn)GetProcAddress(h, "Nfo_GetObjectIDA");
    getObjStrFn   Nfo_GetObjectClassA  = (getObjStrFn)GetProcAddress(h, "Nfo_GetObjectClassA");
    getObjStrFn   Nfo_GetObjectNameA   = (getObjStrFn)GetProcAddress(h, "Nfo_GetObjectNameA");
    openObjFn     Nfo_OpenObject       = (openObjFn)GetProcAddress(h, "Nfo_OpenObject");
    getObjSizeFn  Nfo_GetObjectSize    = (getObjSizeFn)GetProcAddress(h, "Nfo_GetObjectSize");
    readObjFn     Nfo_ReadObject       = (readObjFn)GetProcAddress(h, "Nfo_ReadObject");
    closeObjFn    Nfo_CloseObject      = (closeObjFn)GetProcAddress(h, "Nfo_CloseObject");

    if (!Nfo_CreateObjectIteratorA || !Nfo_FirstA || !Nfo_NextA || !Nfo_DestroyIterator ||
        !Nfo_GetObjectIDA || !Nfo_OpenObject || !Nfo_GetObjectSize || !Nfo_ReadObject ||
        !Nfo_CloseObject) {
        fprintf(stderr, "object API export(s) missing; skipping object extraction\n");
        return 0;
    }

    CreateDirectoryA(objdir, NULL);   /* ok if it already exists */

    /* iterOpts: NFOFLT4's static 0x1002_91e0 blob, {DWORD 0x2a; 0; ...}. */
    unsigned char iterOpts[0x40];
    memset(iterOpts, 0, sizeof(iterOpts));
    *(DWORD*)(iterOpts + 0) = 0x2a;

    void* iter = NULL;
    int rc = Nfo_CreateObjectIteratorA(infobase, "Folio Objects", iterOpts, &iter);
    if (rc || !iter) {
        fprintf(stderr, "no \"Folio Objects\" table (rc=%d) -- 0 objects\n", rc);
        return 0;
    }

    unsigned char objInfo[0x200];
    unsigned char objID[0x80];
    char classBuf[0x400], nameBuf[0x400];
    unsigned long count = 0;

    memset(objInfo, 0, sizeof(objInfo));
    rc = Nfo_FirstA(iter, 0, objInfo);
    while (rc == 0) {
        memset(objID, 0, sizeof(objID));
        int rid = Nfo_GetObjectIDA(infobase, "Folio Objects", objInfo, objID);
        if (rid == 0) {
            classBuf[0] = 0; nameBuf[0] = 0;
            if (Nfo_GetObjectClassA) Nfo_GetObjectClassA(infobase, objID, classBuf);
            if (Nfo_GetObjectNameA)  Nfo_GetObjectNameA(infobase, objID, nameBuf);

            void* handle = NULL;
            int ro = Nfo_OpenObject(infobase, objID, 4, &handle);
            if (ro == 0 && handle) {
                DWORD size = 0;
                Nfo_GetObjectSize(handle, &size);
                unsigned char* buf = (size > 0) ? (unsigned char*)malloc(size) : NULL;
                DWORD off = 0;
                if (buf) {
                    while (off < size) {
                        DWORD want = size - off;
                        if (want > 0x10000) want = 0x10000;
                        DWORD got = 0;
                        int rr = Nfo_ReadObject(handle, buf + off, (int)want, &got);
                        if (rr != 0 || got == 0) break;
                        off += got;
                    }
                }
                Nfo_CloseObject(handle);

                /* choose leaf name: object name (or class_index), then ensure it
                 * carries the magic-derived extension. */
                char base[0x420], safe[0x420], leaf[0x480], path[0x600];
                const char* ext = magic_ext(buf ? buf : (unsigned char*)"", off);
                if (nameBuf[0]) {
                    sanitize(nameBuf, safe, sizeof(safe));
                } else {
                    char tmp[0x440];
                    _snprintf(tmp, sizeof(tmp), "%s_%04lu",
                              classBuf[0] ? classBuf : "object", count);
                    tmp[sizeof(tmp)-1] = 0;
                    sanitize(tmp, safe, sizeof(safe));
                }
                _snprintf(base, sizeof(base), "%s", safe); base[sizeof(base)-1]=0;
                if (ends_with_ext(base, ext))
                    _snprintf(leaf, sizeof(leaf), "%s", base);
                else
                    _snprintf(leaf, sizeof(leaf), "%s.%s", base, ext);
                leaf[sizeof(leaf)-1] = 0;

                _snprintf(path, sizeof(path), "%s/%s", objdir, leaf);
                path[sizeof(path)-1] = 0;
                /* de-dup identical leaf names */
                {
                    FILE* t = fopen(path, "rb");
                    for (int dup = 1; t; dup++) {
                        fclose(t);
                        _snprintf(path, sizeof(path), "%s/%s_%d.%s", objdir, base, dup, ext);
                        path[sizeof(path)-1] = 0;
                        t = fopen(path, "rb");
                    }
                }

                if (buf && off > 0) {
                    FILE* fo = fopen(path, "wb");
                    if (fo) {
                        fwrite(buf, 1, off, fo);
                        fclose(fo);
                        *pTotal += off;
                        count++;
                        fprintf(stderr, "  obj[%lu] class='%s' name='%s' %lu bytes -> %s\n",
                                count, classBuf, nameBuf, (unsigned long)off, path);
                    } else {
                        fprintf(stderr, "  cannot write %s\n", path);
                    }
                }
                free(buf);
            } else if (Nfo_GetErrorA) {
                char* e = Nfo_GetErrorA();
                fprintf(stderr, "  OpenObject('%s') failed: [%s]\n",
                        nameBuf, e ? e : "(null)");
            }
        }
        memset(objInfo, 0, sizeof(objInfo));
        rc = Nfo_NextA(iter, 0, objInfo);
    }
    Nfo_DestroyIterator(iter);
    return count;
}

int main(int argc, char** argv)
{
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOOPENFILEERRORBOX | SEM_NOGPFAULTERRORBOX);
    SetUnhandledExceptionFilter(topFilter);

    if (argc < 2) {
        fprintf(stderr, "usage: nfotext <infobase.nfo> [out.txt] [objdir]\n");
        return 2;
    }
    const char* nfoPath = argv[1];
    const char* objdir  = (argc >= 4) ? argv[3] : NULL;  /* dump embedded objects here */
    if (argc >= 3) {
        g_out = fopen(argv[2], "wb");
        if (!g_out) { fprintf(stderr, "cannot open output %s\n", argv[2]); return 2; }
    } else {
        g_out = stdout;
        _setmode(_fileno(stdout), _O_BINARY);  /* no CRLF translation on body text */
    }

    HMODULE h = LoadLibraryA("nfomgr4.dll");
    if (!h) { fprintf(stderr, "LoadLibrary nfomgr4.dll failed err=%lu\n", GetLastError()); return 3; }

    initFn           Nfo_Initialize;
    createSessionFn  Nfo_CreateSession;
    openFn           Nfo_OpenInfobaseA;
    createBinderFn   Nfo_CreateBinderA;
    getCountFn       Nfo_GetCount;
    readRecFn        Nfo_ReadPageRecordsA;
    closeInfFn       Nfo_CloseInfobase;
    destroyBinderFn  Nfo_DestroyBinder;
    destroySessionFn Nfo_DestroySession;
    termFn           Nfo_Terminate;
    getErrFn         Nfo_GetErrorA;

    GETPROC(Nfo_Initialize,       initFn,           "Nfo_Initialize");
    GETPROC(Nfo_CreateSession,    createSessionFn,  "Nfo_CreateSession");
    GETPROC(Nfo_OpenInfobaseA,    openFn,           "Nfo_OpenInfobaseA");
    GETPROC(Nfo_CreateBinderA,    createBinderFn,   "Nfo_CreateBinderA");
    GETPROC(Nfo_GetCount,         getCountFn,       "Nfo_GetCount");
    GETPROC(Nfo_ReadPageRecordsA, readRecFn,        "Nfo_ReadPageRecordsA");
    GETPROC(Nfo_CloseInfobase,    closeInfFn,       "Nfo_CloseInfobase");
    GETPROC(Nfo_DestroyBinder,    destroyBinderFn,  "Nfo_DestroyBinder");
    GETPROC(Nfo_DestroySession,   destroySessionFn, "Nfo_DestroySession");
    GETPROC(Nfo_Terminate,        termFn,           "Nfo_Terminate");
    Nfo_GetErrorA = (getErrFn)GetProcAddress(h, "Nfo_GetErrorA");

    #define SHOWERR(where) do { \
        if (Nfo_GetErrorA) { char* e = Nfo_GetErrorA(); \
            fprintf(stderr, "%s: [%s]\n", where, e ? e : "(null)"); } } while(0)

    CoInitialize(NULL);  /* NfoFind initialises COM before opening */

    int rc;
    rc = Nfo_Initialize(GetUserDefaultLCID());
    fprintf(stderr, "Nfo_Initialize -> %d\n", rc);
    if (rc) { SHOWERR("Nfo_Initialize"); return 4; }

    void* session = NULL;
    rc = Nfo_CreateSession(&session);
    fprintf(stderr, "Nfo_CreateSession -> %d  session=%p\n", rc, session);
    if (rc) { SHOWERR("Nfo_CreateSession"); Nfo_Terminate(); return 4; }

    /* openOpts: 0x410-byte struct; size + two flags, per NfoFind. */
    unsigned char opts[0x410];
    memset(opts, 0, sizeof(opts));
    *(DWORD*)(opts + 0x00) = 0x410;
    *(DWORD*)(opts + 0x08) = 1;
    *(DWORD*)(opts + 0x0c) = 1;

    void* infobase = NULL;
    rc = Nfo_OpenInfobaseA(session, nfoPath, opts, &infobase);
    fprintf(stderr, "Nfo_OpenInfobaseA(%s) -> %d  infobase=%p\n", nfoPath, rc, infobase);
    if (rc || !infobase) { SHOWERR("Nfo_OpenInfobaseA");
        Nfo_DestroySession(session); Nfo_Terminate(); return 5; }

    /* Binder needs the full-text query so it selects every record in reading
     * order.  arg4 is a char** (pointer to the query-string pointer), per NfoFind. */
    void* binder = NULL, *qbinder = NULL;
    const char* qptr = "[Include:[universe] [fulltext]]";
    rc = Nfo_CreateBinderA(infobase, NULL, 1, &qptr, &binder, &qbinder);
    fprintf(stderr, "Nfo_CreateBinderA -> %d  binder=%p qbinder=%p\n", rc, binder, qbinder);
    if (rc || !binder) { SHOWERR("Nfo_CreateBinderA");
        Nfo_CloseInfobase(infobase); Nfo_DestroySession(session); Nfo_Terminate(); return 6; }

    /* Nfo_GetCount(binder, &countInfo): countInfo is a 0x24-byte struct whose
     * first dword is its size (0x24); the record count lands at offset 4. */
    unsigned char cntbuf[0x24];
    memset(cntbuf, 0, sizeof(cntbuf));
    *(DWORD*)(cntbuf + 0) = 0x24;
    rc = Nfo_GetCount(binder, cntbuf);
    DWORD count  = *(DWORD*)(cntbuf + 4);
    DWORD count8 = *(DWORD*)(cntbuf + 8);
    fprintf(stderr, "Nfo_GetCount -> %d  count[+4]=%lu count[+8]=%lu\n", rc, count, count8);

    rc = Nfo_ReadPageRecordsA(binder, 0, (int)count, (void*)fifCallback, NULL);
    fprintf(stderr, "Nfo_ReadPageRecordsA(0,%lu) -> %d\n", count, rc);
    if (rc) SHOWERR("Nfo_ReadPageRecordsA");

    fflush(g_out);
    if (g_out != stdout) { fclose(g_out); g_out = NULL; }
    fprintf(stderr, "DONE: %llu bytes, %lu text-runs, %lu breaks\n",
            g_bytes, g_text_runs, g_breaks);

    /* Embedded-object dump (infobase still open).  Must run before teardown. */
    if (objdir) {
        unsigned long long objBytes = 0;
        unsigned long nObjs = extract_objects(h, infobase, objdir, Nfo_GetErrorA, &objBytes);
        fprintf(stderr, "OBJECTS: %lu objects, %llu bytes -> %s\n", nObjs, objBytes, objdir);
        printf("%lu objects, %llu bytes\n", nObjs, objBytes);  /* one-line summary on stdout */
        fflush(stdout);
    }

    if (g_bytes == 0 && !objdir) return 7;  /* opened but produced nothing */

    /* All text is written.  Mark done so a teardown fault exits cleanly, then
     * attempt best-effort teardown (it faults inside the engine's local-server
     * COM shutdown under wine -- harmless, caught by topFilter). */
    InterlockedExchange(&g_done, 1);
    Nfo_DestroyBinder(binder);
    Nfo_CloseInfobase(infobase);
    Nfo_DestroySession(session);
    Nfo_Terminate();
    return 0;
}
