import {Format} from "../../Format.js";

export class tar extends Format
{
	name       = "Tape Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Tar";
	ext        = [".tar", ".gtar"];
	magic      = ["TAR - Tape ARchive", /.* tar archive/, /^tar archive$/];
	converters = ["tar", "7z", "UniExtract"];
}
