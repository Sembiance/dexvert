import {xu} from "xu";
import {Format} from "../../Format.js";

export class proDigi extends Format
{
	name          = "ProDigi Tracker Module";
	ext           = [".m", ".pdt"];
	weakExt       = [".m"];
	fileSize      = 99072;
	matchFileSize = true;
	idCheck       = inputFile => !["zc_neutr.ilb"].includes(inputFile.base.toLowerCase());	// These are false positives that recur in the wild
	metaProvider  = ["musicInfo"];
	converters    = ["zxtune123"];
	verify        = ({meta}) => meta.duration>=xu.SECOND;
}
