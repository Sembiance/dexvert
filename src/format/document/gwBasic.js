import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class gwBasic extends Format
{
	name       = "GW-BASIC";
	website    = "http://justsolve.archiveteam.org/wiki/GW-BASIC_tokenized_file";
	ext        = [".bas"];
	magic      = ["GW-BASIC Protected Source"];
	idCheck    = async inputFile => (await fileUtil.readFileBytes(inputFile.absolute, 1, -1))[0]===0x1A;
	converters = ["bascat"];
}
