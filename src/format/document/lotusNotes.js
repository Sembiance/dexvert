import {Format} from "../../Format.js";

export class lotusNotes extends Format
{
	name           = "Lotus Notes Database";
	ext            = [".nsf"];
	forbidExtMatch = true;
	magic          = ["Lotus Notes database"];
	converters     = ["strings"];
}
