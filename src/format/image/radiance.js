import {Format} from "../../Format.js";

export class radiance extends Format
{
	name         = "Radiance HDR";
	website      = "http://fileformats.archiveteam.org/wiki/Radiance_HDR";
	ext          = [".hdr", ".rgbe", ".xyze", ".pic", ".rad"];
	mimeType     = "image/vnd.radiance";
	magic        = ["Radiance RGBE Image Format", "Radiance HDR image data", "Radiance High Dynamic Range bitmap", /^fmt\/591( |$)/];
	metaProvider = ["image"];
	converters   = ["pfsconvert", "convert", "nconvert", `abydosconvert[format:${this.mimeType}]`, "gimp"];
}
