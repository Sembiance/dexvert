import {Format} from "../../Format.js";

export class printMagicCard extends Format
{
	name           = "Print Magic Card";
	ext            = [".pmc"];
	forbidExtMatch = true;
	magic          = ["Print Magic Card"];
	converters     = ["wuimg[format:pmg]"];
}
