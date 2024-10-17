import {Format} from "../../Format.js";

export class moleBoxPacked extends Format
{
	name           = "MoleBox Packed";
	website        = "http://fileformats.archiveteam.org/wiki/AMOS_BASIC_tokenized_file";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Packer: MoleBox"];
	converters     = ["demoleition"];
}
