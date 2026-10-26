import {Format} from "../../Format.js";

export class mdecVideoStream extends Format
{
	name           = "MDEC video stream";
	ext            = [".str"];
	forbidExtMatch = true;
	magic          = [/^MDEC video stream/];
	converters     = ["vibe2avi"];
}
