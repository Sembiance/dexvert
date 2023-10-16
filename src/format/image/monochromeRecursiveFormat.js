import {Format} from "../../Format.js";

export class monochromeRecursiveFormat extends Format
{
	name       = "Monochrome Recursive Format";
	website    = "http://fileformats.archiveteam.org/wiki/MRF_(Monochrome_Recursive_Format)";
	ext        = [".mrf"];
	magic      = ["Monochrome Recursive Format"];
	converters = ["mrftopbm", "nconvert"];
}
