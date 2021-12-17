import {Format} from "../../Format.js";

export class windowsClipboard extends Format
{
	name       = "Windows Clipboard";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_clipboard";
	ext        = [".clp"];
	magic      = ["Windows Clipboard"];
	converters = ["clipbrdWin2k", "nconvert[format:clp]", "irfanView"];
}
