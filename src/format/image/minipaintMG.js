import {Format} from "../../Format.js";

export class minipaintMG extends Format
{
	name           = "Minipaint MG";
	website        = "https://sourceforge.net/p/recoil/bugs/102/";
	ext            = [".mg"];	// fake, doesn't really have an extension
	fileSize       = 4097;
	forbidExtMatch = true;
	magic          = ["Minipaint MG"];
	//weakMagic      = true;	// not sure if it's weak or not (comes from dexmagic), we'll find out
	converters     = ["recoil2png"];
}
