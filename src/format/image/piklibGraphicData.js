import {Format} from "../../Format.js";

export class piklibGraphicData extends Format
{
	name           = "Piklib/BlooMoo graphic data";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = ["Piklib/BlooMoo graphic data"];
	converters     = ["wuimg"];
}
