import {Format} from "../../Format.js";

export class windowsClipboard extends Format
{
	name       = "Windows Clipboard";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_clipboard";
	ext        = [".clp"];
	magic      = ["Windows Clipboard"];
	notes      = "Haven't found a good conversion program. For example DRIVE.CLP is a Windows 3.1 clip file which opens fine in Win2k clipboard viewer. But nconvert and irfanView both convert it wrong and haven't found anything else.";
	converters = ["nconvert[format:clp]", "irfanView"];
}
