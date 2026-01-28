import {Format} from "../../Format.js";

export class bloodLaceCompressedTGA extends Format
{
	name           = "Blood & Lace Compressed TGA";
	ext            = [".tga"];
	forbidExtMatch = true;
	magic          = ["Blood & Lace Compressed TGA"];
	converters     = ["bl_unpack -> dexvert[asFormat:image/tga]"];
}
