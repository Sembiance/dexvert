import {Format} from "../../Format.js";

export class epocMBM extends Format
{
	name       = "EPOC MultiBitmap";
	website    = "http://fileformats.archiveteam.org/wiki/EPOC_MBM";
	ext        = [".mbm"];
	magic      = ["EPOC/Symbian MultiBitMap", /^Psion Series 5 (exported )?multi-bitmap image/, "deark: epocimage (EPOC MBM)", "Psion Series 5 Bitmap file :psion5:"];
	converters = ["deark[module:epocimage]", "nconvert[format:psion5][extractAll]"];
}
