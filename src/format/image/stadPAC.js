import {Format} from "../../Format.js";

export class stadPAC extends Format
{
	name       = "STAD PAC";
	website    = "http://fileformats.archiveteam.org/wiki/STAD_PAC";
	ext        = [".pac", ".seq"];
	mimeType   = "image/x-stad";
	magic      = ["STAD hi-res", "Atari ST STAD bitmap image data", "Stad :stad:", /^fmt\/1653( |$)/];
	converters = ["nconvert[format:stad]", "recoil2png[format:PAC]", `abydosconvert[format:${this.mimeType}]`];
}
