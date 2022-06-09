import {Format} from "../../Format.js";

export class zingDirectoryInfo extends Format
{
	name           = "Zing! Directory Info";
	ext            = [".zing"];
	forbidExtMatch = true;
	magic          = ["Zing! directory info"];
	converters     = ["strings"];
}
