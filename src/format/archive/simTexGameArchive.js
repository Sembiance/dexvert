import {Format} from "../../Format.js";

export class simTexGameArchive extends Format
{
	name           = "SimTex Game Archive";
	ext            = [".lbx"];
	forbidExtMatch = true;
	magic          = ["SimTex LBX game data container", /^geArchive: LBX( |$)/];
	converters     = ["gameextractor[codes:LBX]"];
}
