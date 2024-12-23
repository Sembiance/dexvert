import {Format} from "../../Format.js";

export class xbmcTexturePackage extends Format
{
	name       = "XBMC Texture Package";
	ext        = [".xbt"];
	weakMagic  = true;
	magic      = [/^XBMC texture package/];
	converters = ["xbtfextractor"];
}
