"use strict";
/* eslint-disable max-len, node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

tiptoe(
	function findFormats()
	{
		fileUtil.glob(path.join(__dirname, "..", "lib", "format"), "**/*.js", {nodir : true}, this);
	},
	function generateReadme(formatFilePaths)
	{
		const formats = formatFilePaths.map(formatFilePath => ({family : path.basename(path.dirname(formatFilePath)), ...require(formatFilePath).meta}));
		formats.filterInPlace(f => f.unsupported);

		fs.writeFile(path.join(__dirname, "..", "UNSUPPORTED.md"), `# Unsupported File Formats

The following ${formats.length.toLocaleString()} file formats are NOT currently supported by dexvert.

${formats.map(f => f.family).unique().multiSort(f => f).map(familyid => `

## ${familyid.toProperCase()} (${formats.filter(f => f.family===familyid).length.toLocaleString()})
Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
${formats.filter(f => f.family===familyid).multiSort(f => f.name).map(f => (`${f.family} | ${f.website ? `[${f.name}](${f.website})` : f.name} | ${(f.ext || []).join(" ")} | ${(f.notes || "").replaceAll("\n", " ")}`)).join("\n")}
`).join("\n")}
`, XU.UTF8, this);
	},
	XU.FINISH
);
