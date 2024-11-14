import {Format} from "../../Format.js";
import {_TEXE_MAGIC} from "../document/texe.js";
import {_READMAKE_MAGIC} from "../document/readmake.js";

export class exePackPacked extends Format
{
	name           = "EXEPACK Packed";
	website        = "http://fileformats.archiveteam.org/wiki/EXEPACK";
	ext            = [".exe", ".com"];
	forbidExtMatch = true;
	magic          = ["Packer: EXEPACK", "EXEPACK compressed DOS Executable", "Packer: WordPerfect EXEPack"];
	forbiddenMagic = [..._TEXE_MAGIC, ..._READMAKE_MAGIC];
	packed         = true;
	converters     = ["deark[module:exepack]"];
}
