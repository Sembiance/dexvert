import {xu} from "xu";
import {path} from "std";
import {Program} from "../../Program.js";

const _FORMATS =
{
	bload2color       : {keys : "21", safeExt : ".BIN"},
	bload4color       : {keys : "22", safeExt : ".BIN"},
	compuserveGIF     : {keys : "31", safeExt : ".GIF"},
	compuserveRLE     : {keys : "32", safeExt : ".RLE"},
	drHaloCUT         : {keys : "4", safeExt : ".CUT"},
	doodleCBM         : {keys : "5", safeExt : ".CBM"},
	firstPublisherART : {keys : "61", safeExt : ".ART"},
	firstPublisherMAC : {keys : "62", safeExt : ".MAC"},
	fontasyBLK        : {keys : "71", safeExt : ".BLK"},
	fontasyPIC        : {keys : "72", safeExt : ".PIC"},
	fontasyPV         : {keys : "73", safeExt : ".PV"},	// not supported yet due it asking which clip but program hangs trying to send input
	gemIMG            : {keys : "8", safeExt : ".IMG"},
	iff               : {keys : "9", safeExt : ".IFF"},
	macPaint          : {keys : "A", safeExt : ".MAC"},
	newsMasterSHP     : {keys : "B", safeExt : ".SHP"},
	newsroomCA        : {keys : "C", safeExt : ".CA"},
	pcPaintCLP        : {keys : "D1", safeExt : ".CLP"},
	pcPaintPIC        : {keys : "D2", safeExt : ".PIC"},
	pcPaintbrushPCC   : {keys : "E1", safeExt : ".PCC"},
	pcPaintbrushPCX   : {keys : "E2", safeExt : ".PCX"},
	printMasterSHP    : {keys : "F1", safeExt : ".SHP"},
	printMasterGRA    : {keys : "F2", safeExt : ".GRA"},
	printShopDAT      : {keys : "G1", safeExt : ".DAT"},
	printShopPS       : {keys : "G2", safeExt : ".PS"},
	tiff              : {keys : "H", safeExt : ".TIF"},
	windowsPaint      : {keys : "I", safeExt : ".MSP"}
};

const _OUT_FORMATS =
{
	gif  : {keys : "31", ext : "GIF"},
	tiff : {keys : "h1", ext : "TIF"}
};

export class iconvertDOS extends Program
{
	website = "https://archive.org/details/IConvertV1.10DShareware";
	unsafe  = true;
	loc     = "win2k";	// this is a DOS program but doesn't run in dosbox, so we run it in win2k instead
	bin     = "c:\\dexvert\\ICONVERT\\ICONVERT.COM";
	flags   = {
		format  : "Which format is the input picture",
		outType : "Specify which format to export to. DEFAULT: tiff"
	};
	osData = r => ({
		cwd          : "c:\\out",
		dontMaximize : true,
		script       : `
			$mainWindow = WindowRequire("c:\\dexvert\\ICONVERT\\ICONVERT.COM", "", 10)
			Sleep(1000)

			; ICONVERT will only find files if they have the right extension
			FileMove("c:\\in\\${path.basename(r.inFile())}", "c:\\in\\SAFE${_FORMATS[r.flags.format].safeExt}")
			
			; This line modifies the auto-clip defaults to always be equal to image width and max height of 1024 but sadly it didn't seem to help with auto-clipping (image/fontasyPicture/GREECRD.PIC) but does seem to help with others? maybe? dunno.
			SendSlow("3jc20{ENTER}11024{ENTER}{ESCAPE}00", 350)

			SendSlow("1${_FORMATS[r.flags.format].keys}c:\\in{ENTER}${_OUT_FORMATS[r.flags.outType || "tiff"].keys}11", 300)
			WaitForStableFileSize("c:\\out\\SAFE.${_OUT_FORMATS[r.flags.outType || "tiff"].ext}", ${xu.SECOND}, ${xu.SECOND*5})
			If Not FileExists("c:\\out\\SAFE.${_OUT_FORMATS[r.flags.outType || "tiff"].ext}") Then
				; some formats (image/fontasyPicture/GREECRD.PIC) require auto-clipping weird
				Send("1")
				WaitForStableFileSize("c:\\out\\SAFE.${_OUT_FORMATS[r.flags.outType || "tiff"].ext}", ${xu.SECOND}, ${xu.SECOND*5})
			EndIf
			
			SendSlow("00", 400)
			WinWaitClose($mainWindow, "", 3)`});
	renameOut = true;
	chain     = r => `dexvert[asFormat:image/${r.flags.outType || "tiff"}]`;
}
