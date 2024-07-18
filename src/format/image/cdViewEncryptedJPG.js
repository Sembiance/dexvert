import {Format} from "../../Format.js";

export class cdViewEncryptedJPG extends Format
{
	name           = "CDView Encrypted JPG";
	ext            = [".jpg", ".jpeg"];
	forbidExtMatch = true;
	magic          = ["CDView Encrypted JPG"];
	weakMagic      = true;
	converters     = ["CDView2001"];
}
