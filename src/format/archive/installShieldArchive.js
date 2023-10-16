import {Format} from "../../Format.js";

export class installShieldArchive extends Format
{
	name       = "InstallShield Archive";
	website    = "http://fileformats.archiveteam.org/wiki/InstallShield_archive_(IBT)";
	ext        = [".ibt"];
	magic      = ["InstallShield archive"];
	converters = ["deark[module:is_ibt]"];
}
