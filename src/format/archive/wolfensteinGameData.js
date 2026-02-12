import {Format} from "../../Format.js";

export class wolfensteinGameData extends Format
{
	name           = "Wolfenstein game data";
	ext            = [".spk", ".mpk"];
	forbidExtMatch = true;
	magic          = ["Wolfenstein game data", /^geArchive: SPK_3( |$)/];
	converters     = ["gameextractor[codes:SPK_3]"];
}
