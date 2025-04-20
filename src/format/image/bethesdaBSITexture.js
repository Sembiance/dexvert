import {Format} from "../../Format.js";

export class bethesdaBSITexture extends Format
{
	name       = "Bethesda BSI Texture";
	ext        = [".bsi"];
	magic      = ["Bethesda Image texture"];
	weakMagic  = true;
	converters = ["wuimg"];
}
