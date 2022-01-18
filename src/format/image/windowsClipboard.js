import {Format} from "../../Format.js";

export class windowsClipboard extends Format
{
	name       = "Windows Clipboard";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_clipboard";
	ext        = [".clp"];
	magic      = ["Windows Clipboard"];

	// for deark, we rename out so things like Bitmap.ddb.png get renamed properly, but sometimes WMF files are also extracted, then we end up with out.###.whatever.ddb.png, but alas.
	converters = ["deark[renameOut]", "clipbrdWin2k", "nconvert[format:clp]", "irfanView"];
}
