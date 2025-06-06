import {Format} from "../../Format.js";

export class quakeTexture extends Format
{
	name       = "Quake Texture";
	website    = "http://fileformats.archiveteam.org/wiki/Quake_2_Texture";
	ext        = [".wal"];
	magic      = ["Quake Texture :wal:"];
	converters = ["nconvert[format:wal]", "noesis[type:image]", "irfanView"];
}
