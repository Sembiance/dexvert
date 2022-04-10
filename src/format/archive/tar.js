import {Format} from "../../Format.js";

export class tar extends Format
{
	name           = "Tape Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Tar";
	ext            = [".tar", ".gtar"];
	magic          = ["TAR - Tape ARchive", /.* tar archive/, /^tar archive$/];
	forbiddenMagic = ["TFMX module sound data tar archive"];
	converters     = ["tar", "sevenZip", "UniExtract"];
}
