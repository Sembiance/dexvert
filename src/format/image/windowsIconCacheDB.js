import {xu} from "xu";
import {Format} from "../../Format.js";

export class windowsIconCacheDB extends Format
{
	name           = "Windows IconCacheDB";
	ext            = [".db"];
	forbidExtMatch = true;
	magic          = ["Format: Windows IconCacheDB"];
	safeFilename   = "ShellIconCache";	// required for konvertor to work. But doesn't seem to work for all samples
	converters     = ["konvertor"];
}
