import {Format} from "../../Format.js";

export class acornSpark extends Format
{
	name           = "Acorn Spark Compressed Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Spark";
	ext            = [".spk", ".arc"];
	forbidExtMatch = [".arc"];
	magic          = ["Acorn Spark Archive", "deark: spark (Spark)"];
	converters     = ["deark[module:spark]"];
}
