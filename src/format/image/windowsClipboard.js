import {Format} from "../../Format.js";

export class windowsClipboard extends Format
{
	name       = "Windows Clipboard";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_clipboard";
	ext        = [".clp"];
	magic      = ["Windows Clipboard", "deark: clp"];

	// for deark, we rename out so things like Bitmap.ddb.png get renamed properly, but sometimes WMF files are also extracted, then we end up with out.###.whatever.ddb.png, but alas.
	converters = [
		"deark[module:clp][renameOut]",
		//"clipbrdWin2k",	// No longer works, after removing win2k for win7, but it's ok, handled by deark now
		"nconvert[format:clp]", "irfanView", "hiJaakExpress"
	];
}
