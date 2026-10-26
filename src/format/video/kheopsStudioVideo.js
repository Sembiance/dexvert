import {Format} from "../../Format.js";

export class kheopsStudioVideo extends Format
{
	name           = "Kheops Studio Video";
	ext            = [".ksv"];
	forbidExtMatch = true;
	magic          = ["Kheops Studio Video"];
	converters     = ["vibe2avi"];
}
