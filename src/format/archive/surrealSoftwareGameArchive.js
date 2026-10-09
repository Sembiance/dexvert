import {Format} from "../../Format.js";

export class surrealSoftwareGameArchive extends Format
{
	name           = "Surreal Software Game Archive";
	ext            = [".adu", ".sdu", ".tdu", ".gdu", ".vdu", ".mdu", ".xdu", ".wdu", ".odu", ".qdu1", ".ldu", ".lvl1", ".qdu", ".lvl", ".rrc", ".rsg", ".rlt"];
	forbidExtMatch = true;
	magic          = ["Drakan: Order Of The Flame Saved Game", "Surreal Software game data container", /^geArchive: SDU_SRSC( |$)/];
	weakMagic      = [/^geArchive: SDU_SRSC( |$)/];
	converters     = ["gameextractor[codes:SDU_SRSC]"];
}
