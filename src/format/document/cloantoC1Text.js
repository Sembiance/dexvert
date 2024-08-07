import {Format} from "../../Format.js";

export class cloantoC1Text extends Format
{
	name        = "Cloanto C1-Text Document";
	ext         = [".c1text"];
	magic       = ["Cloanto C1-Text compressed document"];
	unsupported = true;
	notes       = "Have only encountered just 1 file in the wild. If I encounter more, I can get Cloanto C1-Text program, load it into the Amiga and convert it there.";
}
