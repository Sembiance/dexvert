
import {Format} from "../../Format.js";

export class dBASEMultipleIndex extends Format
{
	name           = "dBASE Multiple Index";
	ext            = [".mdx"];
	forbidExtMatch = true;
	magic          = ["dBASE IV Multiple index", "FoxBase MDX"];
	converters     = ["strings"];
}
