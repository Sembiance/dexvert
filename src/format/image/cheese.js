import {Format} from "../../Format.js";

export class cheese extends Format
{
	name       = "Cheese";
	website    = "http://fileformats.archiveteam.org/wiki/Cheese";
	ext        = [".che"];
	mimeType   = "image/x-cheese";
	fileSize   = 20482;
	converters = ["recoil2png", "nconvert", `abydosconvert[format:${this.mimeType}]`, "view64"];
}
