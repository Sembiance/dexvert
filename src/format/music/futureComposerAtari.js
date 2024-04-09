import {Format} from "../../Format.js";

export class futureComposerAtari extends Format
{
	name         = "Future Composer Atari";
	website      = "http://atariki.krap.pl/index.php/FC_%28format_pliku%29";
	ext          = [".fc"];
	magic        = ["Future Composer Atari"];	// kinda weak, just 2 bytes but if I set weakMagic then it relies on extension being correct
	metaProvider = ["musicInfo"];
	converters   = ["asapconv"];
}
