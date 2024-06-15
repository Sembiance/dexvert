import {Format} from "../../Format.js";

export class squeezeIt extends Format
{
	name       = "Squeeze It Archive";
	ext        = [".sqz"];
	magic      = ["Squeeze It compressed archive", "Squeeze It archive data", "SQZ Archiv gefunden (Auflistung ist deaktiviert)"];
	converters = ["squeezeIt"];
}
