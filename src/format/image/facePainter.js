import {Format} from "../../Format.js";

export class facePainter extends Format
{
	name     = "Face Painter";
	website  = "http://fileformats.archiveteam.org/wiki/Face_Painter";
	ext      = [".fcp", ".fpt"];
	mimeType = "image/x-face-painter";
	fileSize = 10004;

	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`, "view64"]
}
