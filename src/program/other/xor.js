import {xu} from "xu";
import {Program} from "../../Program.js";
import {base64Decode} from "std";

export class xor extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	flags   = {
		hex : "Two letter capitalized hexadecimal string representing the byte to XOR with (e.g. 'AB')"
	};
	bin       = Program.binPath("xor/xor");
	args      = async r => [r.inFile(), await r.outFile("outfile"), r.flags.hex];
	renameOut = true;
}
