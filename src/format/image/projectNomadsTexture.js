import {Format} from "../../Format.js";

export class projectNomadsTexture extends Format
{
	name           = "Project Nomads Texture";
	ext            = [".ntx"];
	forbidExtMatch = true;
	magic          = ["Project Nomads Texture", /^geViewer: NPK_0KPN_NTX_1XTN( |$)/];
	converters     = ["gameextractor[renameOut][codes:NPK_0KPN_NTX_1XTN]"];
}
