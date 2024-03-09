import {Format} from "../../Format.js";

export class lightWaveScene extends Format
{
	name           = "LightWave Scene";
	website        = "http://fileformats.archiveteam.org/wiki/LightWave_Scene";
	ext            = [".lws", ".scn"];
	forbidExtMatch = true;
	magic          = ["LightWave 3D Scene"];
	untouched      = true;
	metaProvider   = ["text"];
}
