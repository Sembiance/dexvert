import {xu} from "xu";
import {Format} from "../../Format.js";

export class pes extends Format
{
	name         = "PES Embroidery File";
	website      = "http://fileformats.archiveteam.org/wiki/PES";
	ext          = [".pes"];
	magic        = ["Brother/Babylock/Bernina Home Embroidery Format", /^fmt\/1957( |$)/];
	metaProvider = ["image"];
	notes        = xu.trim`
		It's a vector format, but uniconvertor just embeds a PNG into the resulting SVG file.
	 	Imagemagick's convert can produce .svg versions, but it doesn't output all the original lines and no color.
		So we convert to both SVG and PNG with convert.
		NOTE: Some of these files produce HUGE resulting files and the process can take a good amoung of time to complete.`;

	converters = ["convert & convert[outType:svg]"];
}

