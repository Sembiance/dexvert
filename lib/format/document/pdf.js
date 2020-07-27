"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "Portable Document Format",
	website          : "http://fileformats.archiveteam.org/wiki/PDF",
	ext              : [".pdf"],
	mimeType         : "application/pdf",
	magic            : ["Adobe Portable Document Format", "PDF document", /Acrobat PDF.* Portable Document Format$/]
};

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "pdfinfo"}),
	(state, p) =>
	{
		if(!state.run.pdfinfo)
			return p.util.flow.noop;

		const infoLines = (state.run.pdfinfo[0] || "").trim().split("\n").filterEmpty();
		if(infoLines.length===0)
			return p.util.flow.noop;
		
		const NUMS = ["pages", "pagerot"];
		const BOOLS = ["tagged", "userproperties", "suspects", "javascript", "encrypted", "optimized"];
		const metaData = {};
		infoLines.forEach(infoLine =>
		{
			const infoProps = (infoLine.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {}).groups;
			if(!infoProps)
				return;

			const propKey = infoProps.name.toLowerCase().replaceAll(" ", "");
			if(propKey==="filesize")
				return;

			metaData[propKey] = NUMS.includes(propKey) ? +infoProps.val : (BOOLS.includes(propKey) ? infoProps.val==="yes" : infoProps.val);
		});

		if(Object.keys(metaData).length>0)
		{
			state.input.meta.pdf = metaData;
			state.processed = true;
		}
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);
