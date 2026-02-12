import {Format} from "../../Format.js";

export class finalLiberationGameArchive extends Format
{
	name           = "Final Liberation/Holistic Design game archive";
	ext            = [".muk"];
	forbidExtMatch = true;
	magic          = ["Final Liberation: Warhammer Epic 40K game data archive", /^geArchive: MUK_MUKFILE( |$)/];
	converters     = ["gameextractor[codes:MUK_MUKFILE]"];
}
