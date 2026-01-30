import {Format} from "../../Format.js";

export class asyncProfessionalFax extends Format
{
	name           = "Async Profesional Fax";
	website        = "http://fileformats.archiveteam.org/wiki/Async_Professional_Fax";
	ext            = [".apf"];
	forbidExtMatch = true;
	magic          = ["Async Professional Fax"];
	converters     = ["wuimg[format:apf]"];
}
