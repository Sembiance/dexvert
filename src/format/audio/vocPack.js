import {Format} from "../../Format.js";

export class vocPack extends Format
{
	name           = "VOCPACK Compressed Audio";
	website        = "https://www.rarewares.org/rrw/vocpack.php";
	ext            = [".vp", ".vc"];
	forbidExtMatch = true;
	magic          = ["VOCPACK lossless compressed audio"];
	converters     = ["vocpak"];
}
