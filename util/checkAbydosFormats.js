"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	httpUtil = require("@sembiance/xutil").http,
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	domino = require("domino"),
	tiptoe = require("tiptoe");

const IGNORED_MIMES =
[
	// Handled natively
	"image/apng", "image/vnd.mozilla.apng",

	// Handled by another mime type
	"image/jpeg2000",
	"image/x-eps",
	"image/x-stos-picturepacker",
	"image/x-portable-anymap",
	
	// Handled by another program
	"video/x-anim",

	// Chosen not to handle at all
	"application/x-doom-wad"
];

tiptoe(
	function downloadWebPage()
	{
		httpUtil.get("http://snisurset.net/code/abydos/supported.html", this.parallel());
		fileUtil.glob(path.join(__dirname, "..", "src", "format"), "**/*.js", {nodir : true}, this.parallel());
	},
	function checkFormats(formatsHTMLRaw, imageFormatFilePaths)
	{
		const supportedMimeTypes = imageFormatFilePaths.map(imageFormatFilePath => (require(imageFormatFilePath).meta || {}).mimeType).filterEmpty();

		let unsupportedCount = 0;
		const doc = domino.createWindow(formatsHTMLRaw.toString("utf8")).document;
		Array.from(doc.querySelectorAll("table.grid tr")).forEach(row =>
		{
			const cells = Array.from(row.querySelectorAll("td"), cell => (cell.textContent || "").trim());
			if(cells.length!==8 || cells[1].length===0 || cells[3].toLowerCase()==="no")
				return;
			
			const mimeTypes = cells[1].split(",").map(v => v.trim()).subtractAll(IGNORED_MIMES);
			if(mimeTypes.length===0 || mimeTypes.some(mimeType => supportedMimeTypes.includes(mimeType)))
				return;

			XU.log`Unsupported abydos format: ${cells[0]} ${mimeTypes.join(", ")}`;
			unsupportedCount++;
		});

		XU.log`\nUnsupported count: ${unsupportedCount}`;

		this();
	},
	XU.FINISH
);
