import {Format} from "../../Format.js";

export class nocturnePOD extends Format
{
	name           = "Nocturne POD";
	ext            = [".pod"];
	forbidExtMatch = true;
	magic          = [/^geArchive: POD_POD2( |$)/, "dragon: POD2 "];
	converters     = ["gameextractor[codes:POD_POD2]", "dragonUnpacker[types:POD2]"];
}
