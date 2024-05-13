import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class gwBasic extends Format
{
	name       = "GW-BASIC";
	website    = "http://justsolve.archiveteam.org/wiki/GW-BASIC_tokenized_file";
	ext        = [".bas"];
	magic      = ["GW-BASIC Protected Source"];
	idCheck    = async inputFile =>
	{
		// if we have a .bas extension then safe enough to try
		if(inputFile.ext.toLowerCase()===".bas")
			return true;

		// Othwise ensure we end in 0x1A (some files have trailing 0x00 bytes, so we allow that here too, so long as the 0x1A is in the last 256 bytes)
		const endBytes = (await fileUtil.readFileBytes(inputFile.absolute, Math.min(256, inputFile.size), -(Math.min(256, inputFile.size)))).reverse();
		for(const b of endBytes)
		{
			if(b===0x1A)
				return true;

			if(b===0x00)
				continue;

			break;
		}

		return false;
	};
	converters = ["bascat"];
}
