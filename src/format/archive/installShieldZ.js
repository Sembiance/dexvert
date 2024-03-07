import {Format} from "../../Format.js";

export class installShieldZ extends Format
{
	name       = "InstallShield Z Archive";
	website    = "http://fileformats.archiveteam.org/wiki/InstallShield_Z";
	ext        = [".z"];
	magic      = ["InstallShield Z archive", "Stirling Archiv gefunden"];
	converters = ["isextract", "UniExtract[type:i3comp extraction]", "UniExtract[type:STIX extraction]", "deark[module:is_z]"];
}
