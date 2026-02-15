import {Format} from "../../Format.js";

export class vbm extends Format
{
	name           = "VDC BitMap";
	website        = "http://fileformats.archiveteam.org/wiki/VBM_(VDC_BitMap)";
	ext            = [".vbm", ".bm"];
	forbidExtMatch = [".bm"];
	magic          = ["VDC BitMap", "deark: vbm", /^fmt\/1906( |$)/];
	converters     = ["deark[module:vbm][matchType:magic]", "recoil2png[format:VBM,BM]", "view64"];
}
