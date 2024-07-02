import {Format} from "../../Format.js";

export class videoFX2Effect extends Format
{
	name           = "VideoFX2 Effect";
	ext            = [".vfx"];
	forbidExtMatch = true;
	magic          = ["VideoFX2 Effect"];
	untouched      = true;
	metaProvider   = ["text"];
}
