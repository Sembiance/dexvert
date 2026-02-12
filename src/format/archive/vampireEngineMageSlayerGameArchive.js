import {Format} from "../../Format.js";

export class vampireEngineMageSlayerGameArchive extends Format
{
	name           = "Vampire Engine MageSlayer game archive";
	ext            = [".vpk"];
	forbidExtMatch = true;
	magic          = ["Vampire Engine MageSlayer game data archive", /^geArchive: VPK_MAGE( |$)/];
	converters     = ["gameextractor[codes:VPK_MAGE]"];
}
