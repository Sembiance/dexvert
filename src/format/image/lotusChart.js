import {Format} from "../../Format.js";

export class lotusChart extends Format
{
	name           = "Lotus 1-2-3 Chart";
	website        = "http://fileformats.archiveteam.org/wiki/Lotus_1-2-3_Chart";
	ext            = [".pic"];
	forbidExtMatch = true;
	mimeType       = "image/x-lotus-1-2-3-chart";
	magic          = ["Lotus Picture"];
	converters     = [`abydosconvert[format:${this.mimeType}]`, "hiJaakExpress", "corelPhotoPaint"];
}
