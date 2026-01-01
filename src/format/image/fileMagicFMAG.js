import {Format} from "../../Format.js";

export class fileMagicFMAG extends Format
{
	name           = "FileMagic FMAG";
	ext            = [".mag"];
	forbidExtMatch = true;
	magic          = ["FileMagic :fmag:"];
	converters     = ["nconvert[format:fmag]"];
}
