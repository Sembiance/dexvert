import {xu} from "xu";
import {Program} from "../../Program.js";

export class bl_unpack extends Program
{
	website   = "https://codecs.multimedia.cx/2026/01/blood-lace-unpacker/";
	bin       = Program.binPath("bl_unpack/bl_unpack");
	args      = async r => [r.inFile(), await r.outFile("out")];
	renameOut = true;
}
