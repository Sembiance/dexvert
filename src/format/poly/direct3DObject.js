import {Format} from "../../Format.js";

export class direct3DObject extends Format
{
	name        = "Direct3D Object";
	website     = "http://fileformats.archiveteam.org/wiki/X_(DirectX)";
	ext         = [".x"];
	magic       = ["Microsoft Direct3D Object"];
	unsupported = true;
}
