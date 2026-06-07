import {xu} from "xu";
import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {identify} from "../identify.js";
import {fileUtil} from "xutil";

export class document extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const {ids : identifications} = await identify(dexFile);

		// If the output file is a PDF, then we check it's bounding box, because often programs will produce an 'empty' PDF file when it fails to convert (such as fileMerlin)
		if(identifications.some(id => id.from==="dexvert" && id.family==="document" && id.formatid==="pdf"))
		{
			const {meta : gsPDFMeta} = await Program.runProgram("gsPDFInfo", dexFile, {xlog, autoUnlink : true});
			if(gsPDFMeta.boundingBoxes.filter(v => v.trim()==="%%BoundingBox: 0 0 0 0").length===gsPDFMeta.boundingBoxes.length)
			{
				xlog.warn`Document failed output file verification due to zero bounding box: ${gsPDFMeta.boundingBoxes.join("   ")}`;
				return false;
			}
		}
		
		// if txt is detected and <1k, verify that there is actually content and not just "empty" lines
		if(identifications.some(id => id.from==="dexvert" && id.family==="text" && id.formatid==="txt") && dexFile.size<xu.KB && (await fileUtil.readTextFile(dexFile.absolute)).trim().length===0)
		{
			xlog.warn`Document failed utput file verification due to detected as text/txt and contianing just whitespace.`;
			return false;
		}

		return {identifications};
	}
}
