import {Format} from "../../Format.js";

export class synu extends Format
{
	name           = "Synthetic Universe Image";
	website        = "http://fileformats.archiveteam.org/wiki/Synu";
	ext            = [".synu", ".syn"];
	forbidExtMatch = true;
	magic          = ["Synu bitmap", "Synthetic Universe :synu:"];
	weakMagic      = true;
	converters     = ["imconv[format:synu]", "nconvert[format:synu]"];
}
