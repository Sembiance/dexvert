import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class ascSoundMaster extends Format
{
	name         = "ASC Sound Master";
	website      = "http://fileformats.archiveteam.org/wiki/ASC_Sound_Master_module";
	ext          = [".asc"];
	idCheck      = async inputFile => inputFile.size>3 && (await fileUtil.readFileBytes(inputFile.absolute, 4))[3]===0x00;	// every ASC file I've encountered has a 0x00 as the 3rd byte
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];

	// Because we just have an extension, sometimes ASCII files will convert and end up being just garbage. So ensure we have at least a 1 second long music file result
	verify = ({meta}) => meta.duration>=xu.SECOND;
}
