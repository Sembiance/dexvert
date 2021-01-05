"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	fs = require("fs"),
	{formats : unsupportedFormats} = require("../lib/format/unsupported.js"),
	tiptoe = require("tiptoe");

const SAMPLES_DIR_PATH = path.join(__dirname, "..", "test", "sample");

tiptoe(
	function findFormatFiles()
	{
		fileUtil.glob(path.join(__dirname, "..", "lib", "format"), "**/*.js", {nodir : true}, this.parallel());
		fileUtil.glob(SAMPLES_DIR_PATH, "**", {nodir : true}, this.parallel());
	},
	function generateReadme(formatFilePaths, fileSamplePaths)
	{
		const fileSampleCounts = {};
		fileSamplePaths.forEach(fileSamplePath =>
		{
			const subPathPaths = path.relative(SAMPLES_DIR_PATH, fileSamplePath).split(path.sep);
			const fullFormatid = `${subPathPaths[0]}/${subPathPaths[1]}`;
			if(!fileSampleCounts.hasOwnProperty(fullFormatid))
				fileSampleCounts[fullFormatid] = 0;
			fileSampleCounts[fullFormatid]++;
		});

		const allFormats = formatFilePaths.map(formatFilePath => ({family : path.basename(path.dirname(formatFilePath)), formatid : path.basename(formatFilePath, ".js"), ...require(formatFilePath).meta}));
		Object.forEach(unsupportedFormats, (family, subFormats) => Object.forEach(subFormats, (formatid, subFormat) => allFormats.push({family, formatid, unsupported : true, ...subFormat})));

		[{name : "SUPPORTED", formats : allFormats.filter(f => f.name && !f.unsupported)}, {name : "UNSUPPORTED", formats : allFormats.filter(f => f.name && f.unsupported)}].parallelForEach((o, subcb) =>
		{
			fs.writeFile(path.join(__dirname, "..", `${o.name}.md`), `# ${o.name.toProperCase()} File Formats

The following ${o.formats.length.toLocaleString()} file formats are ${o.name.toLowerCase()} by dexvert.

${o.name==="UNSUPPORTED" ? `They are still **identified** by dexvert, just not processed in any way.` : ""}

${o.formats.map(f => f.family).unique().multiSort(f => f).map(familyid => `

## ${familyid.toProperCase()} (${o.formats.filter(f => f.family===familyid).length.toLocaleString()})
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
${o.formats.filter(f => f.family===familyid).multiSort(f => f.name).map(f =>
	{
		const noteParts = [];
		const fullFormatid = `${f.family}/${f.formatid}`;
		if(fileSampleCounts.hasOwnProperty(fullFormatid))
			noteParts.push(`[${fileSampleCounts[fullFormatid].toLocaleString()} sample file${fileSampleCounts[fullFormatid]===1 ? "" : "s"}](https://telparia.com/fileFormatSamples/${f.family}/${f.formatid}/)`);
		
		const noteText = (f.notes || "").replaceAll("\n", " ").trim();
		if(noteText && noteText.length>0)
			noteParts.push(noteText);
		return (`${f.family} | ${f.website ? `[${f.name}](${f.website})` : f.name} | ${(f.ext || []).join(" ")} | ${noteParts.join(" - ")}`);
	}).join("\n")}
`).join("\n")}
`, XU.UTF8, subcb);
		}, this);
	},
	XU.FINISH
);

