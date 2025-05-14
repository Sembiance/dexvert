import {Format} from "../../Format.js";
import {_TEXE_MAGIC} from "../document/texe.js";
import {_READMAKE_MAGIC} from "../document/readmake.js";

export class exePackPacked extends Format
{
	name           = "EXEPACK Packed";
	website        = "http://fileformats.archiveteam.org/wiki/EXEPACK";
	ext            = [".exe", ".com"];
	forbidExtMatch = true;
	magic          = [
		// generic
		"Packer: EXEPACK", "EXEPACK compressed DOS Executable", "Packer: WordPerfect EXEPack",

		// specific
		"16bit DOS DemoMaker Executable presentation (v1.x)"	// NOTE: archive/exePackPacked/SAMPLE.EXE - Could create a format that records of video and press spacebar a bunch for like 30 seconds at 1 second intervals, but meh.
	];
	forbiddenMagic = [..._TEXE_MAGIC, ..._READMAKE_MAGIC];
	packed         = true;
	converters     = ["deark[module:exepack]"];
}
