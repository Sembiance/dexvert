import {Format} from "../../Format.js";

export class ediInstallArchive extends Format
{
	name       = "EDI Install Archive";
	website    = "http://fileformats.archiveteam.org/wiki/EDI_Install_archive";
	ext        = ["$00", "$01", "$02", "$04", "$05"];	// etc.
	magic      = ["EDI Install archive"];
	converters = ["ediInstallArchiveExtractor"];
}
