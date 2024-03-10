import {Format} from "../../Format.js";

export class digitalElevationMap extends Format
{
	name        = "Digital Elevation Map";
	website     = "http://fileformats.archiveteam.org/wiki/DEM";
	ext         = [".dem"];
	magic       = ["Vista Digital Elevation Map", /^x-fmt\/369( |$)/];
	unsupported = true;	// AccuTrans3D failed all. So did https://github.com/domlysz/BlenderGIS   and cinema4D427 only opened 1 of my samples, poorly.
}
