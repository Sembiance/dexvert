import {Format} from "../../Format.js";

export class kissCel extends Format
{
	name       = "Kisekae Set System Cell";
	website    = "http://fileformats.archiveteam.org/wiki/KiSS_CEL";
	ext        = [".cel", ".kcf"];
	mimeType   = "image/x-kiss-cel";
	magic      = ["KiSS CEL bitmap", "KISS/GS", "deark: animator_pic", "KiSS Cel :cel:"];
	converters = ["deark[module:animator_pic]", "recoil2png", "nconvert[format:cel]", `abydosconvert[format:${this.mimeType}]`, "gimp"];
}
