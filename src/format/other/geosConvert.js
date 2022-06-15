import {Format} from "../../Format.js";

export class geosConvert extends Format
{
	name           = "GEOS ConVerT";
	ext            = [".cvt"];
	forbidExtMatch = true;
	website        = "http://unusedino.de/ec64/technical/formats/cvt.html";
	magic          = ["GEOS ConVerT container format"];
	converters     = ["strings"];
}
