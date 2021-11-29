import {Format} from "../../Format.js";

export class clarionTopspeed extends Format
{
	name           = "Clarion Topspeed Data File";
	ext            = [".tps"];
	forbidExtMatch = true;
	magic          = ["Clarion Topspeed Data file"];
	converters     = ["strings"];
}
