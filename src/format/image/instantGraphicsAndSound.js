import {xu} from "xu";
import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";
import {fileUtil} from "xutil";

export class instantGraphicsAndSound extends Format
{
	name        = "Instant Graphics and Sound";
	website     = "http://fileformats.archiveteam.org/wiki/Instant_Graphics_and_Sound";
	ext         = [".igs", ".ig", ".igm"];
	magic       = ["Instant Graphics and Sound", ...TEXT_MAGIC];
	weakMagic   = true;
	idCheck     = async inputFile => (await fileUtil.readFileBytes(inputFile.absolute, Math.min(xu.KB, inputFile.size))).indexOfX([0x47, 0x23])!==-1;
	unsupported = true;	// only 46 unique files on discmaster: https://discmaster.textfiles.com/search?detection=4723%3F%3F3e*&dedup=dedup
	notes       = "No known converter yet. Seen a recent resurgence in interest in 2024";
}
