import {Format} from "../../Format.js";

export class borlandTurboVisionResource extends Format
{
	name           = "Borland Turbo Vision Resource";
	ext            = [".res", ".tvr"];
	forbidExtMatch = true;
	magic          = ["Borland Turbo Vision Resource"];
	converters     = ["strings"];
}
