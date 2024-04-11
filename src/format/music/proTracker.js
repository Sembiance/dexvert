import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class proTracker extends Format
{
	name         = "Pro Tracker";
	website      = "http://fileformats.archiveteam.org/wiki/Pro_Tracker_v1.xx_module";
	ext          = [".pt1", ".pt2", ".pt3"];
	idCheck      = async inputFile => ![".pt1", ".pt2"].includes(inputFile.ext.toLowerCase()) || (inputFile.size>5 && (await fileUtil.readFileBytes(inputFile.absolute, 2, 3)).indexOfX([0x00, 0x00])===0);	// every .pt1/.pt2 file I've encountered has a 0x00 0x00 at offset 3
	magic        = ["Spectrum Pro Tracker 3 chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul"];
}
