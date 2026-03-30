import {Format} from "../../Format.js";

export class crowdEngineAudioArchive extends Format
{
	name           = "Crowd Engine Audio Archive";
	ext            = [".pck"];
	forbidExtMatch = true;
	magic          = ["archive:Crowd.PkwOpener"];
	converters     = ["GARbro[types:archive:Crowd.PkwOpener]"];
}
