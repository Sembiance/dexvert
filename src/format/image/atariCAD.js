import {Format} from "../../Format.js";

export class atariCAD extends Format
{
	name       = "Atari CAD";
	website    = "http://fileformats.archiveteam.org/wiki/AtariCAD";
	ext        = [".drg"];
	mimeType   = "image/x-atari-cad";
	fileSize   = 6400;
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
