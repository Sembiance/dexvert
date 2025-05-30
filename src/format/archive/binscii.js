import {xu} from "xu";
import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";
import {flexMatch} from "../../identify.js";
import {fileUtil} from "xutil";

const BINSCII_MAGIC = ["BinSCII", "binscii", "deark: binscii"];

export class binscii extends Format
{
	name       = "BinSCII";
	website    = "http://fileformats.archiveteam.org/wiki/BinSCII";
	ext        = [".bsc", ".bsq"];
	magic      = [...BINSCII_MAGIC, ...TEXT_MAGIC];
	weakMagic  = TEXT_MAGIC;
	converters = ["binsciiPrepare -> deark[module:binscii]"];

	idCheck = async (inputFile, detections) =>
	{
		// If we have a BinSCII match, we don't need to keep checking
		if(detections.some(detection => BINSCII_MAGIC.some(matchAgainst => flexMatch(detection.value, matchAgainst))))
			return true;

		// Otherwise we are a TEXT file and some binscii files have several lines of text metadata at the top (lode.killer.bsc), or whitespace at the start of every line (girl1.bsc)
		// So read in the first X bytes, convert to lines and check if we have a line that without whitespace equals: FiLeStArTfIlEsTaRt
		const buf = await fileUtil.readFileBytes(inputFile.absolute, Math.min(xu.KB*100, inputFile.size));
		const lines = (new TextDecoder().decode(buf)).split("\n");
		for(const line of lines)
		{
			if(line.trim()==="FiLeStArTfIlEsTaRt")
				return true;
		}

		return false;
	};
}
