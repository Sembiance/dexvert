import {Format} from "../../Format.js";

export class cWorthyOverlay extends Format
{
	name           = "C-Worthy Machine Overlay";
	ext            = [".ovl"];
	forbidExtMatch = true;
	magic          = ["C-Worthy Machine Dependant Overlay"];
	converters     = ["strings"];
}
