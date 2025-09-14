import {Format} from "../../Format.js";

export class aseprite extends Format
{
	name       = "Asperite";
	website    = "http://fileformats.archiveteam.org/wiki/Aseprite";
	ext        = [".ase", ".aseprite"];
	mimeType   = "image/x-aseprite";
	magic      = ["Aseprite Animated sprite", /^Aseprite asset file/];
	converters = [`abydosconvert[format:${this.mimeType}]`];
	verify     = ({meta}) => meta.height>4 && meta.width>4 && meta.width<2000 && meta.height<2000;	// fairly modern format, probably could skip supporting this format, but only 1 mis-identified file on discmaster so far, so meh
}
