import {Format} from "../../Format.js";

export class whyPic extends Format
{
	name       = "WhyPic";
	website    = "http://fileformats.archiveteam.org/wiki/WhyPic";
	ext        = [".ypc"];
	magic      = ["WhyPic bitmap"];
	converters = ["konvertor[matchType:magic][hasExtMatch]"];
}
