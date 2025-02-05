import {Format} from "../../Format.js";

export class crowdANIMGameDataFormat extends Format
{
	name           = "CROWD ANIM game data format";
	website        = "https://ja.wikipedia.org/wiki/CROWD";
	ext            = [".cwl"];
	forbidExtMatch = true;
	magic          = ["CROWD ANIM game data format", "Crowd Anim Engine"];
	converters     = ["gameViewerLinux[plugin:crowd_anim_engine]"];
}
