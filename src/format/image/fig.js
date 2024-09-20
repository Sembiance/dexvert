import {Format} from "../../Format.js";

export class fig extends Format
{
	name         = "XFig";
	website      = "http://fileformats.archiveteam.org/wiki/Fig";
	ext          = [".fig"];
	magic        = ["FIG image text", "FIG vector drawing", "image/x-xfig"];
	notes        = "It's a vector format, but embedded bitmaps don't convert to SVG. So we convert to both SVG and PNG.";
	keepFilename = true;
	auxFiles     = (input, otherFiles) => (otherFiles.length>0 ? otherFiles : false);
	converters   = ["fig2dev & fig2dev[outType:png]"];
}
