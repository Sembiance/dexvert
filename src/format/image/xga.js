import {Format} from "../../Format.js";

export class xga extends Format
{
	name       = "XGA";
	website    = "http://fileformats.archiveteam.org/wiki/XGA_(Falcon)";
	ext        = [".xga"];
	mimeType   = "image/x-xga";
	fileSize   = [153_600, 368_640];
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
