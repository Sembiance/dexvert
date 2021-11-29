import {Format} from "../../Format.js";

export class amosMenuBank extends Format
{
	name           = "AMOS Menu Bank";
	ext            = [".abk"];
	forbidExtMatch = true;
	magic          = ["AMOS Menu Bank"];
	converters     = ["strings"];
}
