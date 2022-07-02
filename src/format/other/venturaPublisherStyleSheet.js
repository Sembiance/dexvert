import {Format} from "../../Format.js";

export class venturaPublisherStyleSheet extends Format
{
	name           = "Ventur Publisher Style Sheet";
	ext            = [".sty"];
	forbidExtMatch = true;
	magic          = ["Ventura Publisher Style sheet"];
	converters     = ["strings"];
}
