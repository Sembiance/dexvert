import {Format} from "../../Format.js";

export class ani extends Format
{
	name       = "Microsoft Windows Animated Cursor";
	website    = "http://fileformats.archiveteam.org/wiki/ANI";
	ext        = [".ani"];
	mimeType   = "application/x-navi-animation";
	magic      = ["Windows Animated Cursor", /^RIFF .* animated cursor$/];
	converters = ["deark -> *joinAsGIF"];
}
