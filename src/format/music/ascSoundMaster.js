import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class ascSoundMaster extends Format
{
	name         = "ASC Sound Master";
	website      = "http://fileformats.archiveteam.org/wiki/ASC_Sound_Master_module";
	ext          = [".asc", ".as0"];
	idCheck      = async inputFile => inputFile.ext.toLowerCase()!==".asc" || (inputFile.size>4 && (await fileUtil.readFileBytes(inputFile.absolute, 4))[3]===0x00);	// every ASC file I've encountered has a 0x00 as the 4th byte
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;	// due to being an extension only match
}
