import {Format} from "../../Format.js";

export class highwayPursuitGameDataArchive extends Format
{
	name           = "Highway Pursuit game data archive";
	ext            = [".hvd", ".hfd", ".hod", ".hsd", ".hmd", ".hgd"];
	forbidExtMatch = true;
	magic          = ["Highway Pursuit game data archive", /^geArchive: HD_HPDT( |$)/];
	converters     = ["gameextractor[codes:HD_HPDT]"];
}
