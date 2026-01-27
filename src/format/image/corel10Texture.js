import {Format} from "../../Format.js";

export class corel10Texture extends Format
{
	name           = "Corel 10 Texture";
	ext            = [".tex"];
	forbidExtMatch = true;
	magic          = ["Corel 10 Texture"];
	converters     = ["foremost"];
}
