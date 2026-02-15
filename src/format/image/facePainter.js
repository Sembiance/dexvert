import {Format} from "../../Format.js";

export class facePainter extends Format
{
	name       = "Face Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Face_Painter";
	ext        = [".fcp", ".fpt"];
	magic      = ["FacePainter :fpt:"];
	mimeType   = "image/x-face-painter";
	fileSize   = 10004;
	converters = ["recoil2png[format:FCP,FPT]", `abydosconvert[format:${this.mimeType}]`, "view64", "nconvert[format:fpt]"];
}
