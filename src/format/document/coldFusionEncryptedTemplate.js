import {Format} from "../../Format.js";

export class coldFusionEncryptedTemplate extends Format
{
	name           = "ColdFusion Encrypted Template";
	website        = "http://fileformats.archiveteam.org/wiki/ColdFusion";
	ext            = [".cfm"];
	forbidExtMatch = true;
	magic          = ["ColdFusion Template"];
	converters     = ["cfdecrypt"];
}
