import {Format} from "../../Format.js";

export class turboPascalOverlay extends Format
{
	name           = "Turbo Pascal Overlay";
	ext            = [".ovr"];
	forbidExtMatch = true;
	magic          = ["Turbo Pascal Overlay"];
	converters     = ["strings"];
}
