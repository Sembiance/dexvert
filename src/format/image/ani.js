import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class ani extends Format
{
	name       = "Microsoft Windows Animated Cursor";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_Animated_Cursor";
	ext        = [".ani"];
	mimeType   = "application/x-navi-animation";
	magic      = ["Windows Animated Cursor", /^RIFF .* animated cursor/, "Generic RIFF file ACON", "deark: riff (Windows animated cursor)", /^fmt\/386( |$)/];
	meta       = async inputFile =>
	{
		const inputData = await fileUtil.readFileBytes(inputFile.absolute, 512);	// hopefully the anih chunk is in the first 512 bytes
		
		// Look for the 'anih' subchunk and then grab the displayRate: https://web.archive.org/web/20130530192915/http://oreilly.com/www/centers/gff/formats/micriff
		const anihLoc = inputData.indexOfX("anih");
		if(anihLoc===null)
			return {};
		
		let displayRate = inputData.getUInt32LE(anihLoc + 36);
		if(displayRate>60)
			displayRate = 6;	// If the displayRate is >60 then fallback to 10FPS

		// Assume an NTSC 60Hz display, that's a 16.66ms minimum delay (+1) between frames
		return {fps : xu.SECOND/(16.66*(displayRate+1))};
	};
	converters = dexState => [`deark[module:riff] -> convert -> *ffmpeg[fps:${dexState.meta.fps || 8}][outType:gif]`, `nconvert[format:ani][extractAll] -> *ffmpeg[fps:${dexState.meta.fps || 8}][outType:gif]`, "nconvert[format:ani]"];
}
