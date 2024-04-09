import {xu} from "xu";
import {Format} from "../../Format.js";

export class proDigi extends Format
{
	name          = "ProDigi Tracker Module";
	ext           = [".m", ".pdt"];
	weakExt       = [".m"];
	fileSize      = 99_072;
	matchFileSize = true;
	metaProvider  = ["musicInfo"];
	converters    = ["zxtune123"];
	verify        = ({meta}) => meta.duration>=xu.SECOND;
}
