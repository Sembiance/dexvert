import {Format} from "../../Format.js";

export class kissCel extends Format
{
	name       = "Kisekae Set System Cell";
	website    = "http://fileformats.archiveteam.org/wiki/KiSS_CEL";
	ext        = [".cel", ".kcf"];
	mimeType   = "image/x-kiss-cel";
	magic      = ["KiSS CEL bitmap", "KISS/GS", "KiSS Cel :cel:"];
	converters = ["nconvert[format:cel]", "wuimg[format:ckiss][matchType:magic]", `abydosconvert[format:${this.mimeType}]`, "gimp"];
}
