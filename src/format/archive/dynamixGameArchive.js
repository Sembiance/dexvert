import {Format} from "../../Format.js";

export class dynamixGameArchive extends Format
{
	name           = "Dynamix Game Archive";
	ext            = [".dyn"];
	forbidExtMatch = true;
	magic          = ["Dynamix game data archive", "Dynamix Volume File game data archive", /^geArchive: DYN_DYNAMIX( |$)/];
	converters     = ["gameextractor[codes:DYN_DYNAMIX]"];
}
