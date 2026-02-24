import {Format} from "../../Format.js";

export class isiGMotorGameDataArchive extends Format
{
	name           = "ISI gMotor game data archive";
	ext            = [".gtl"];
	forbidExtMatch = true;
	magic          = [/^ISI gMotor .*game data archive$/, /^geArchive: (MAS|GTR_GMOTORMAS)( |$)/];
	converters     = ["gameextractor[codes:MAS,GTR_GMOTORMAS]"];
}
