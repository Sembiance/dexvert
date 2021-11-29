import {Format} from "../../Format.js";

export class ibmPCOverlay extends Format
{
	name           = "IBM PC Overlay";
	ext            = [".ovl"];
	forbidExtMatch = true;
	magic          = ["IBM PC Overlay"];
	converters     = ["strings"];
}
