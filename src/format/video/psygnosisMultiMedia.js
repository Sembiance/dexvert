import {Format} from "../../Format.js";

export class psygnosisMultiMedia extends Format
{
	name        = "Psygnosis MultiMedia Video";
	website     = "https://wiki.multimedia.cx/index.php?title=PMM";
	ext         = [".pmm"];
	magic       = ["PMM video"];
	unsupported = true;
	notes       = "Couldn't locate a converter";
}
