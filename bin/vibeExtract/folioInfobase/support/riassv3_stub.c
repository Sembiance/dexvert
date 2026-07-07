/* Vibe coded by Claude
 *
 * riassv3_stub.c -- stub Folio Rights-server plug-in (riassv3.dll).
 *
 * The Folio 4.2 server (fcsrv3b.dll) gates opening a rights-managed infobase by
 * LoadLibrary'ing the rights server named in the infobase's rights record
 * (here "riassv3.dll") and calling its single export rmRunTimeNfoAccess.  The
 * caller treats the 16-bit return value as the verdict:  0 == access granted,
 * non-zero == denied (see fcsrv3b RVA 0x37754: `mov di,ax; test di,di`).
 *
 * Folio "DRM" is a rights GATE only -- the record content is never encrypted --
 * so returning 0 (full access, not expired) lets the plain content decode
 * normally.  rmRunTimeNfoAccess is stdcall with 8 args (callee `ret 0x20`).
 */
#include <windows.h>

BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID r)
{
    (void)h; (void)r;
    if (reason == DLL_PROCESS_ATTACH) DisableThreadLibraryCalls(h);
    return TRUE;
}

/* Always grant.  Signature matches the engine's stdcall(8) call convention.
 * Args are left untouched: the caller reads only the return code to decide
 * grant/deny; the reference server (rights3.dll) returns its verdict the same
 * way (return value in ax, epilog `ret 0x20`). */
__declspec(dllexport) short WINAPI
rmRunTimeNfoAccess(void *a1, void *a2, void *a3, void *a4,
                   void *a5, unsigned a6, void *a7, unsigned a8)
{
    (void)a1; (void)a2; (void)a3; (void)a4;
    (void)a5; (void)a6; (void)a7; (void)a8;
    return 0;   /* 0 == granted / full access / not expired */
}
