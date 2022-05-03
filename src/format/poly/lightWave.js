import {Format} from "../../Format.js";

export class lightWave extends Format
{
	name        = "LightWave 3D Object";
	website     = "http://fileformats.archiveteam.org/wiki/LightWave_Object";
	ext         = [".lwo", ".lw", ".lightwave"];
	magic       = ["IFF data, LWOB 3-D object", "LightWave 3D Object", "IFF data, LWLO 3-D layered object"];
	unsupported = true;
}
