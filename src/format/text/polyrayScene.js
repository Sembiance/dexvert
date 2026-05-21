import {Format} from "../../Format.js";

export class polyrayScene extends Format
{
	name           = "Polyray Scene";
	ext            = [".pi", ".inc"];
	forbidExtMatch = true;
	magic          = ["Polyray Scene"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];	// unsupported = true;  mv to poly if choose to support. ~331 unique files on discmaster, mostly just the samples that came with the render itself: https://discmaster.textfiles.com/search?extension=pi&detection=*506f6c7972*&dedup=dedup
}
