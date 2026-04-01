import {Format} from "../../Format.js";

export class maxonMagicSoundSample extends Format
{
	name           = "MaxonMAGIC Sound Sample";
	ext            = [".hsn"];
	forbidExtMatch = true;
	magic          = ["MaxonMAGIC Sound sample"];
	converters     = ["vibe2wav[renameOut]"];
}
