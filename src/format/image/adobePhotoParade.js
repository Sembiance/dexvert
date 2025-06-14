import {Format} from "../../Format.js";

export class adobePhotoParade extends Format
{
	name           = "Adobe Photo Parade";
	ext            = [".php"];
	forbidExtMatch = true;
	magic          = ["Adobe PhotoParade :aphp:"];
	converters     = ["nconvert[extractAll][format:aphp]"];
}
