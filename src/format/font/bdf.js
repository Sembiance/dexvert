import {Format} from "../../Format.js";

export class bdf extends Format
{
	name         = "Glyph Bitmap Distribution Format";
	website      = "http://fileformats.archiveteam.org/wiki/BDF";
	ext          = [".bdf"];
	magic        = ["X11 BDF font", "Glyph Bitmap Distribution Format font", "application/x-font-bdf"];
	metaProvider = ["fc_scan"];
	converters   = ["bdftopcf"];
}
