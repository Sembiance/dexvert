import {Format} from "../../Format.js";

export class characterStudioThumbnail extends Format
{
	name           = "Character Studio thumbnail";
	ext            = [".bip"];
	forbidExtMatch = true;
	magic          = ["Character Studio (thumbnail) :bip:", "Character Studio Biped motion"];
	converters     = ["nconvert[format:bip]"];
}
