import {Format} from "../../Format.js";

export class koalaMicroillustrator extends Format
{
	name         = "Koala Microillustrator";
	website      = "http://fileformats.archiveteam.org/wiki/Koala_MicroIllustrator";
	ext          = [".pic"];
	forbiddenExt = [".rm4"];	// Sometimes rambrandt rm4 files are identified as Koala, while similar, they are not the same but they are similar enough that recoil2png will convert it with a .pic extension, poorly
	magic        = ["Koala Micro Illustrator bitmap"];
	notes        = "APOLLO.PIC and STARWAR.PIC don't seem to be handled by recoil or view64, they may be invalid/corrupt.";
	converters   = ["recoil2png", "view64"];
}
