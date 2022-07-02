import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class ultraCardStack extends Format
{
	name           = "UltraCard Stack";
	magic          = ["UltraCard Stack"];
	forbiddenMagic = TEXT_MAGIC;
	converters     = ["strings"];
}
