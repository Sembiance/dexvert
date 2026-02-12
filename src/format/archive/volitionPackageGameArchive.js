import {Format} from "../../Format.js";

export class volitionPackageGameArchive extends Format
{
	name           = "Volition Package game archive";
	ext            = [".vpp", ".vp"];
	forbidExtMatch = true;
	magic          = ["Volition Package - Red Faction game data archive", "Volition Package game archive data", /^geArchive: (VPP|VPP_2|VP_VPVP)( |$)/];
	converters     = ["gameextractor[codes:VPP_2,VPP,VP_VPVP]"];
}
