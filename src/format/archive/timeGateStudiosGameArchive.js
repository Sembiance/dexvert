import {Format} from "../../Format.js";

export class timeGateStudiosGameArchive extends Format
{
	name           = "TimeGate Studios game archive";
	ext            = [".rwd"];
	forbidExtMatch = true;
	magic          = ["TimeGate Studios game data archive", /^geArchive: RWD_TGCK( |$)/];
	converters     = ["gameextractor[codes:RWD_TGCK]"];
}
