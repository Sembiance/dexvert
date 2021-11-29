
import {Format} from "../../Format.js";

export class amigaGuideIndex extends Format
{
	name           = "Amigaguide Index";
	ext            = [".index"];
	forbidExtMatch = true;
	magic          = ["Amigaguide Index"];
	converters     = ["strings"];
}
