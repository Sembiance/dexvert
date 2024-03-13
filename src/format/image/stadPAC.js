import {Format} from "../../Format.js";

export class stadPAC extends Format
{
	name       = "STAD PAC";
	website    = "http://fileformats.archiveteam.org/wiki/STAD_PAC";
	ext        = [".pac", ".seq"];
	mimeType   = "image/x-stad";
	magic      = ["STAD hi-res", "Atari ST STAD bitmap image data", /^fmt\/1653( |$)/];
	converters = ["nconvert", "recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
