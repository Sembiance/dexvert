import {Format} from "../../Format.js";

export class nascarHeatGameArchive extends Format
{
	name           = "NASCAR Heat game archive";
	ext            = [".trk", ".car"];
	forbidExtMatch = true;
	magic          = ["NASCAR Heat game data archive", /^geArchive: RES_0TSR( |$)/];
	converters     = ["gameextractor[codes:RES_0TSR]"];
}
