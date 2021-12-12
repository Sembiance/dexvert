import {Format} from "../../Format.js";

export class itsInternational extends Format
{
	name           = "ITS International Module";
	ext            = [".int"];
	forbidExtMatch = true;
	magic          = ["ITS international module"];
	converters     = ["strings"];
}
