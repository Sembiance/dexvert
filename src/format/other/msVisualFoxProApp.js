import {Format} from "../../Format.js";

export class msVisualFoxProApp extends Format
{
	name           = "MS Visual FoxPro App";
	ext            = [".app", ".fxp"];
	forbidExtMatch = true;
	magic          = ["Generated application MS Visual FoxPro 7"];
	converters     = ["strings"];
}
