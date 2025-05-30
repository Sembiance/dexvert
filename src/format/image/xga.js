import {Format} from "../../Format.js";

export class xga extends Format
{
	name       = "XGA";
	website    = "http://fileformats.archiveteam.org/wiki/XGA_(Falcon)";
	ext        = [".xga"];
	magic      = ["deark: falcon_xga"];
	mimeType   = "image/x-xga";
	fileSize   = [153_600, 368_640];
	converters = ["recoil2png", "deark[module:falcon_xga]", `abydosconvert[format:${this.mimeType}]`];
}
