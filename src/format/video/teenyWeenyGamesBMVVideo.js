import {Format} from "../../Format.js";

export class teenyWeenyGamesBMVVideo extends Format
{
	name           = "Teeny Weeny Games BMV Video";
	ext            = [".bmv"];
	forbidExtMatch = true;
	magic          = ["Teeny Weeny Games BMV Video"];
	converters     = ["vibe2avi"];
}
