import {Format} from "../../Format.js";

export class pixArt extends Format
{
	name       = "PixArt";
	website    = "http://fileformats.archiveteam.org/wiki/PixArt";
	ext        = [".pix"];
	magic      = ["PixArt bitmap"];
	converters = ["recoil2png"];
}
