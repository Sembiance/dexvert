import {Format} from "../../Format.js";

export class lightWave extends Format
{
	name        = "LightWave 3D Object";
	ext         = [".lwo", ".lw", ".lightwave"];
	magic       = ["IFF data, LWOB 3-D object", "LightWave 3D Object"];
	unsupported = true;
}
