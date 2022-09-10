import {Format} from "../../Format.js";

export class extendedMOD extends Format
{
	name         = "Extended MOD";
	website      = "http://fileformats.archiveteam.org/wiki/Extended_MOD";
	ext          = [".emd"];
	magic        = ["Extended MOD module", "Extended MOD sound data"];
	unsupported  = true;
}
