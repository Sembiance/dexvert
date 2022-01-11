import {xu} from "xu";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {path} from "std";

export class amigaBitmapFontContentDetector extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		// https://archive.org/details/amiga-rom-kernel-reference-manual-libraries-3rd-edition/page/698/mode/1up
		// http://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node05DA.html
		// http://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node062F.html

		// font name starts at offset 58 and is a max of 32 characters
		if(r.f.input.size<90)
			return;

		const buf = await fileUtil.readFileBytes(r.inFile({absolute : true}), 90);

		// file id should be equal to DFH_ID or 0x0f80
		if(buf[50]!==0x0F || buf[51]!==0x80)
			return;

		let fontName = "";
		for(let i=58;i<90 && buf[i]!==0;i++)
			fontName += String.fromCharCode(buf[i]);
		
		// usually the font name is <fontName><fontSize>
		// but sometimes the fontName is missing and sometimes both are missing
		// so if we have length>0 then ensure that either the fontName or the fontSize is there
		if(fontName.length>0 && !fontName.endsWith(r.f.input.base) && !fontName.startsWith(path.basename(r.f.input.dir)))
			return;
			
		r.meta.detections.push(Detection.create({value : "amigaBitmapFontContent", from : "single", file : r.f.input}));
	};
	renameOut = false;
}
