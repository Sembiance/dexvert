import {Format} from "../../Format.js";

export class duStar extends Format
{
	name       = "Atari DU* Image";
	website    = "http://fileformats.archiveteam.org/wiki/DU*";
	ext        = [".du1", ".du2", ".duo"];
	mimeType   = "image/x-atari-duo";
	fileSize   = 113_600;
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
