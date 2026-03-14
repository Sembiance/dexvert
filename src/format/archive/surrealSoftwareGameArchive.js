import {Format} from "../../Format.js";

export class surrealSoftwareGameArchive extends Format
{
	name           = "Surreal Software Game Archive";
	ext            = [".adu", ".sdu", ".tdu", ".gdu", ".vdu", ".mdu", ".xdu", ".wdu", ".odu", ".qdu1", ".ldu", ".lvl1", ".qdu", ".lvl", ".rrc"];
	forbidExtMatch = true;
	magic          = ["Surreal Software game data container", /^geArchive: SDU_SRSC( |$)/];
	converters     = ["gameextractor[codes:SDU_SRSC]"];
}
