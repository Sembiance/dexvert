import {Format} from "../../Format.js";

export class videoFX2Script extends Format
{
	name           = "VideoFX2 Script";
	ext            = [".script"];
	forbidExtMatch = true;
	magic          = ["VideoFX2 Script"];
	untouched      = true;
	metaProvider   = ["text"];
}
