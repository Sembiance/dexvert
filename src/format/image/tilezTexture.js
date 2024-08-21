import {Format} from "../../Format.js";

export class tilezTexture extends Format
{
	name           = "Tilez texture";
	ext            = [".til"];
	forbidExtMatch = true;
	magic          = ["Tilez texture"];
	converters     = ["foremost"];
}
