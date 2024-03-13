import {Format} from "../../Format.js";

export class installShieldArchive extends Format
{
	name       = "InstallShield Archive";
	website    = "http://fileformats.archiveteam.org/wiki/InstallShield_archive_(IBT)";
	ext        = [".ibt"];
	magic      = ["InstallShield archive", "InstallShield based SZDD compressed"];
	converters = ["deark[module:is_ibt]"];
}
