import {Format} from "../../Format.js";

export class akaiSample extends Format
{
	name           = "AKAI Sample";
	ext            = [".a1s", ".a3s"];
	forbidExtMatch = true;
	magic          = ["AKAI Sample"];
	weakMagic      = true;
	converters     = ["dd[bs:190][skip:1] -> sox[type:raw][rate:20k][channels:1][encoding:signed][bits:16]"];
}
