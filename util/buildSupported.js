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
		formats.filterInPlace(f => f.name && !f.unsupported);

		fs.writeFile(path.join(__dirname, "..", "SUPPORTED.md"), `# Supported File Formats

The following ${formats.length.toLocaleString()} file formats are support by dexvert.

Family | Name | Extensions | Notes
------ | ---- | ---------- | -----
${formats.multiSort([f => f.family, f => f.name]).map(f => (`${f.family} | ${f.website ? `[${f.name}](${f.website})` : f.name} | ${(f.ext || []).join(" ")} | ${(f.notes || "").replaceAll("\n", " ")}`)).join("\n")}
`, XU.UTF8, this);
	},
	XU.FINISH
);
