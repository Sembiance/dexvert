import {Format} from "../../Format.js";

export class imagesMusicSystem extends Format
{
	name         = "Images Music System";
	website      = "http://fileformats.archiveteam.org/wiki/Images_Music_System";
	ext          = [".ims"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp", "zxtune123"];
}
