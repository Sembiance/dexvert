import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaSEAD extends Format
{
	name             = "Electronic Arts Sound hEADer";
	website          = "http://fileformats.archiveteam.org/wiki/Electronic_Arts_TGV";
	confidenceAdjust = () => -10;	// Reduce by 10 so that video/eaTQI matches first
	magic            = ["Electronic Arts Sound hEADer", "vgmstream: ea_1snh "];
	converters       = ["vgmstream[types:ea_1snh]"];
}
