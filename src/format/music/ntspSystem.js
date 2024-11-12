import {xu} from "xu";
import {Format} from "../../Format.js";

export class ntspSystem extends Format
{
	name         = "NTSP-system";
	ext          = [".two"];
	matchPreExt  = true;
	magic        = ["NTSP-system"];
	idCheck      = inputFile => inputFile.name!=="Funy_128";
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:NTSP-system]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
