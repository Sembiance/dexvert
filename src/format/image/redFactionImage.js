import {Format} from "../../Format.js";

export class redFactionImage extends Format
{
	name           = "Red Faction Image";
	ext            = [".vbm"];
	forbidExtMatch = true;
	magic          = [/^geViewer: VPP_VBM_VBM( |$)/];
	keepFilename   = true;
	converters     = ["gameextractor[renameOut][codes:VPP_VBM_VBM][skipVerify]"];
}
