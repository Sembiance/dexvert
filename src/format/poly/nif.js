import {Format} from "../../Format.js";

export class nif extends Format
{
	name       = "NetImmerse NIF";
	website    = "http://fileformats.archiveteam.org/wiki/NIF";
	ext        = [".nif"];
	magic      = ["NetImmerse file format", "NetImmerse Format", "GameBryo file format", "Gamebryo game engine file"];
	converters = ["nif2glb"];	// this broke: blender[format:nif]
}
