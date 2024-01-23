import {Format} from "../../Format.js";

export class drawIt extends Format
{
	name          = "DrawIt";
	website       = "http://fileformats.archiveteam.org/wiki/DrawIt_(Atari)";
	ext           = [".dit"];
	fileSize      = 3845;
	matchFileSize = true;
	fallback      = true;
	converters    = ["recoil2png"];
}
