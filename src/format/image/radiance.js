import {Format} from "../../Format.js";

export class radiance extends Format
{
	name           = "Radiance HDR";
	website        = "http://fileformats.archiveteam.org/wiki/Radiance_HDR";
	ext            = [".hdr", ".rgbe", ".xyze", ".pic", ".rad"];
	weakExt        = [".pic"];
	mimeType       = "image/vnd.radiance";
	magic          = ["Radiance RGBE Image Format", "Radiance HDR image data", "Radiance High Dynamic Range bitmap", "piped hdr sequence (hdr_pipe)", "HDRI :hdri:", /^fmt\/591( |$)/];
	metaProvider   = ["image"];
	converters     = ["pfsconvert", "convert[strongMatch]", "iconvert[strongMatch]", "nconvert[format:hdri][strongMatch]", "noesis[type:image]", `abydosconvert[format:${this.mimeType}]`, "gimp[strongMatch]"];
	verify         = ({meta}) => meta.colorCount>1;
}
