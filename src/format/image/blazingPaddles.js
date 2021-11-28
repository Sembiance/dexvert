import {Format} from "../../Format.js";

export class blazingPaddles extends Format
{
	name       = "Blazing Paddles";
	website    = "http://fileformats.archiveteam.org/wiki/Blazing_Paddles";
	ext        = [".pi"];
	mimeType   = "image/x-blazing-paddles";
	fileSize   = [10240, 10242];
	converters = ["recoil2png", "nconvert", `abydosconvert[format:${this.mimeType}]`, "view64"];
}
