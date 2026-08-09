import {xu} from "xu";
import {Format} from "../../Format.js";

export class optiksCOM extends Format
{
	name           = "OPTIKS COM";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["OPTIKS Quick View / Self Scrolling COM", "deark: optiks_com"];
	converters     = ["deark[module:optiks_com][charOutType:image]"];
}
