import {Format} from "../../Format.js";

export class winFax extends Format
{
	name       = "WinFax";
	website    = "http://fileformats.archiveteam.org/wiki/WinFax_Fax_Image";
	ext        = [".fxr", ".fxs", ".fxm"];
	magic      = ["WinFax Pro multipage document", "WinFax Sent / Received document", "WinFAX :fxs:", /^fmt\/1995( |$)/];
	converters = ["nconvert[format:fxs]"];
}
