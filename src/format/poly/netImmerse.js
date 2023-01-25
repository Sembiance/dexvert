import {Format} from "../../Format.js";

export class netImmerse extends Format
{
	name        = "NetImmerse File";
	website     = "http://fileformats.archiveteam.org/wiki/NIF";
	ext         = [".nif"];
	magic       = ["NetImmerse file format", "GameBryo file format", "Gamebryo game engine file"];
	unsupported = true;
}
