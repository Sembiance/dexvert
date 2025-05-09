import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class galaxyMusicSystem extends Format
{
	name         = "Galaxy Music System";
	website      = "https://moddingwiki.shikadi.net/wiki/Jazz_2_Music_Format";
	ext          = [".j2b"];
	magic        = ["Galaxy Music System", "Jazz Jackrabbit 2 Music data"];
	idCheck      = async inputFile => inputFile.size>=12 && (await fileUtil.readFileBytes(inputFile.absolute, 4, 8)).getUInt32LE()===inputFile.size;
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
