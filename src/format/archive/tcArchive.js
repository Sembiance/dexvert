import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class tcArchive extends Format
{
	name    = "The Compressor TC Aarchive";
	website = "http://justsolve.archiveteam.org/wiki/The_Compressor_(John_Lauro)";
	ext     = [".arc", ".tc"];
	magic   = ["deark: tc_trs80"];
	idCheck = async (inputFile, _detections, {xlog}) =>
	{
		// header format: https://dev.discmaster2.textfiles.com/view/11868/2014.01.www.rtsi.com.tar/www.rtsi.com/OS9/OS9_6X09/ARCHIVERS/unTC.lzh/untc.c
		if(inputFile.size<19)
			return false;

		const header = await fileUtil.readFileBytes(inputFile.absolute, 18);
		if(header[0]!==0x01 || header[14]!==0x01)
			return false;
		
		// Used to do this check too, but deark is pretty good at checking other bytes to ensure things are proper, and since my check below isn't 100% safe, bypass it.
		// fail if the first file uncompressed size is larger than 50x out entire archive size
		//if(((header[15]*0x10000)+header.getUInt16BE(16))>(inputFile.size*50))	// eslint-disable-line unicorn/numeric-separators-style
		//	return false;

		return true;
	};
	converters = ["deark[module:tc_trs80]"];
}
