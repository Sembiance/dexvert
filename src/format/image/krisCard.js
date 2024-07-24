import {xu} from "xu";
import {Format} from "../../Format.js";

export class krisCard extends Format
{
	name           = "KrisCard";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["16bit COM self displaying KrisCard"];
	converters     = [`dosEXEScreenshot[timeout:${xu.SECOND*10}]`];
}
