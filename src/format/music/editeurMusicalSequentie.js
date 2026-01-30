import {xu} from "xu";
import {Format} from "../../Format.js";

export class editeurMusicalSequentie extends Format
{
	name         = "Editeur Musical Sequentie";
	ext          = [".ems"];
	matchPreExt  = true;
	metaProvider = ["musicInfo"];
	magic        = ["Electronic Music System v6 module"];
	converters   = ["uade123[player:EMS-6]", "uade123[player:EMS]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
