import {Format} from "../../Format.js";

export class CADDrawDrawing extends Format
{
	name           = "TommySoftware CAD/Draw Drawing";
	website        = "http://fileformats.archiveteam.org/wiki/CAD/DRAW";
	ext            = [".t4g", ".t3g", ".t2g", ".mpg"];
	forbidExtMatch = true;
	magic          = ["TommySoftware CAD/Draw drawing", "CAD/Draw TVG"];
	converters     = r => [({".mpg" : "MPG_T2G", ".t2g" : "T2G_T3G", ".t3g" : "T3G_T4G"}[r.f.input.ext.toLowerCase()] || "CADDraw")];
}
