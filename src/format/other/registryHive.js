import {Format} from "../../Format.js";

export class registryHive extends Format
{
	name           = "Windows Registry Hive";
	ext            = [".hiv", ".dat"];
	forbidExtMatch = true;
	magic          = ["Windows NT Registry Hive", "MS Windows registry file", "Windows 9x Registry Hive"];
	converters     = ["hivexml"];
}
