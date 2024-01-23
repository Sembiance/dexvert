import {Format} from "../../Format.js";

export class daVinci extends Format
{
	name     = "DaVinci";
	website  = "http://fileformats.archiveteam.org/wiki/DaVinci";
	ext      = [".img"];
	mimeType = "image/x-davinci";

	// abydosconvert will also convert these, but abydos will take any garbage .img file and produce garbage output. recoil2png is a little better
	converters = ["recoil2png"];
}
