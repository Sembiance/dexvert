import {Format} from "../../Format.js";

export class exePackPacked extends Format
{
	name       = "EXEPACK Packed";
	website    = "http://fileformats.archiveteam.org/wiki/EXEPACK";
	magic      = ["Packer: EXEPACK", "EXEPACK compressed DOS Executable", "Packer: WordPerfect EXEPack"];
	packed     = true;
	converters = ["deark[module:exepack]"];
}
