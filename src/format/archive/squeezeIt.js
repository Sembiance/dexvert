import {Format} from "../../Format.js";

export class squeezeIt extends Format
{
	name           = "Squeeze It Archive";
	ext            = [".sqz", ".exe"];
	forbidExtMatch = [".exe"];
	magic          = ["Squeeze It compressed archive", "Squeeze It archive data", "SQZ Archiv gefunden (Auflistung ist deaktiviert)", "Squeeze self extracting archive"];
	converters     = ["squeezeIt"];
}
