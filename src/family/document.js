import {Family} from "../Family.js";
import {runUtil} from "xutil";

export class document extends Family
{
	async verify(dexState, dexFile)
	{
		const xlog = dexState.xlog;
		const {identify} = await import("../identify.js");
		const identifications = await identify(dexFile, {xlog : xlog.clone("error")});

		// if it's not a PDF, just accept the result
		if(!identifications.some(id => id.from==="dexvert" && id.family==="document" && id.formatid==="pdf"))
			return true;
		
		// If the output file is a PDF, then we check it's bounding box, because often programs will produce an 'empty' PDF file when it fails to convert (such as fileMerlin)
		const {stderr : bboxRaw} = await runUtil.run("gs", ["-dBATCH", "-dNOPAUSE", "-dQUIET", "-sDEVICE=bbox", dexFile.absolute]);
		const boundingBoxLines = bboxRaw.split("\n").filter(v => v.startsWith("%%BoundingBox:"));
		if(boundingBoxLines.filter(v => v.trim()==="%%BoundingBox: 0 0 0 0").length===boundingBoxLines.length)
		{
			xlog.warn`Document failed verification due to zero bounding box ${bboxRaw}`;
			return false;
		}

		return {identifications};
	}
}
