import {Format} from "../../Format.js";

export class bytessence extends Format
{
	name           = "Bytessence Install Maker";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: Bytessence Install Maker"];
	converters     = ["vibeExtract"];
}
