import {Family} from "../Family.js";
import {Program} from "../Program.js";
import {rpcidentify} from "../identify.js";

export class document extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const identifications = await rpcidentify(dexFile);

		// if it's not a PDF, just accept the result
		if(!identifications.some(id => id.from==="dexvert" && id.family==="document" && id.formatid==="pdf"))
			return true;
		
		// If the output file is a PDF, then we check it's bounding box, because often programs will produce an 'empty' PDF file when it fails to convert (such as fileMerlin)
		const {meta : gsPDFMeta} = await Program.runProgram("gsPDFInfo", dexFile, {xlog, autoUnlink : true});
		if(gsPDFMeta.boundingBoxes.filter(v => v.trim()==="%%BoundingBox: 0 0 0 0").length===gsPDFMeta.boundingBoxes.length)
		{
			xlog.warn`Document failed verification due to zero bounding box: ${gsPDFMeta.boundingBoxes.join("   ")}`;
			return false;
		}

		return {identifications};
	}
}
