import {Format} from "../../Format.js";

export class zpPackedGXL extends Format
{
	name           = "ZP Packed GXL";
	ext            = [".zp"];
	forbidExtMatch = true;
	magic          = ["ZP Packed"];
	weakMagic      = true;
	converters     = ["dd[bs:34][skip:1] -> ttdecomp -> deark[module:gxlib]"];
}
