import {xu} from "xu";
import {Format} from "../../Format.js";

export class cbmBasic extends Format
{
	name           = "Commodore BASIC";
	website        = "http://fileformats.archiveteam.org/wiki/Commodore_BASIC_tokenized_file";
	ext            = [".prg", ".bas"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;	// Allow packedC64PRG to take priority
	magic          = ["Commodore 64 BASIC V2 program"];
	idCheck        = inputFile => inputFile.size<(xu.KB*500);	// Commodore BASIC programs are likely to be smaller than 500KB
	converters     = ["detox64", "deark[module:basic_c64]"];
}
