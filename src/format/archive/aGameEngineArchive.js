import {Format} from "../../Format.js";

export class aGameEngineArchive extends Format
{
	name           = "A-Game Engine Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PAK_AGAMEENGINE( |$)/];
	converters     = ["gameextractor[codes:PAK_AGAMEENGINE]"];
}
