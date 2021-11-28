import {Format} from "../../Format.js";

export class daVinci extends Format
{
	name     = "DaVinci";
	website  = "http://fileformats.archiveteam.org/wiki/DaVinci";
	ext      = [".img"];
	mimeType = "image/x-davinci";

	// abydosconvert will also convert these, but unlike recoil2png, abydos will take any garbage .img file and produce garbage output
	converters = ["recoil2png"];
}
