import {Format} from "../../Format.js";

export class adorageAnimation extends Format
{
	name           = "Adorage Animation";
	ext            = [".awm"];
	forbidExtMatch = true;
	magic          = ["Adorage Animation"];
	converters     = ["vibe2avi"];
}
