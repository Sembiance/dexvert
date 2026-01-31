import {Format} from "../../Format.js";

export class digitalTerrainElevationData extends Format
{
	name           = "Digital Terrain Elevation Data";
	website        = "http://fileformats.archiveteam.org/wiki/DTED";
	ext            = [".dt0", ".dt1", ".dt2", ".dted", ".avg", ".min", ".max"];
	forbidExtMatch = [".avg", ".min", ".max"];
	magic          = [/^x-fmt\/314( |$)/];
	converters     = ["tkimgConvert"];
}
