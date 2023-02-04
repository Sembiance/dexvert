import {Format} from "../../Format.js";

export class visualNovelDPK extends Format
{
	name           = "Visual Novel DPK Archive";
	website        = "http://fileformats.archiveteam.org/wiki/DPK";
	ext            = [".dpk"];
	forbidExtMatch = true;
	magic          = ["Visual Novel DPK Archive"];
	converters     = ["undpk"];
}
