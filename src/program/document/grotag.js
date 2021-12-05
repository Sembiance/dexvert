/*
import {Program} from "../../Program.js";

export class grotag extends Program
{
	website = "http://grotag.sourceforge.net/";
	package = "app-text/grotag";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	domino = require("domino"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website       : "http://grotag.sourceforge.net/",
	package : "app-text/grotag",
};

exports.bin = () => "grotag";

// Grotag requires absolute paths. Might be due to the way I call the jar file, not sure.
exports.args = (state, p, r, inPath=state.input.absolute, outPath=state.output.absolute) => (["-w", inPath, outPath]);

// Grotag can hang at 100% on some guides such as sample bootgauge.guide
exports.runOptions = () => ({timeout : XU.MINUTE*3, killSignal : "SIGTERM"});

// The CSS produced by grotag includes this ugly big great outline on all links. Let's get rid of it
exports.post = (state, p, r, cb) =>
{
	// grotag creates a seperate CSS file and all HTML files include that. We are gonna inline the CSS into each HTML file and delete the CSS file and move the resulting HTML files up a directory
	const cssFilePath = path.join(state.output.absolute, "amigaguide.css");

	tiptoe(
		function findHTMLFiles()
		{
			fileUtil.glob(state.output.absolute, "**/*.html", {nodir : true}, this);
		},
		function loadCSSAndHTMLFiles(htmlFilePaths)
		{
			const cssFileExists = fileUtil.existsSync(cssFilePath);
			if(htmlFilePaths.length===0 || !cssFileExists)
				return cssFileExists ? fileUtil.unlink(cssFilePath, err => this.finish(err)) : this.finish();
				
			this.data.htmlFilePaths = htmlFilePaths;
			fs.readFile(cssFilePath, XU.UTF8, this.parallel());
			htmlFilePaths.parallelForEach((htmlFilePath, subcb) => fs.readFile(htmlFilePath, XU.UTF8, subcb), this.parallel());
		},
		function saveModifiedHTML(cssRaw, htmlFilesRaw)
		{
			// The CSS file often has a ton of trailing null bytes, get rid of those. Also all links have this annoying solid gray outline, get rid of that too.
			const cssData = cssRaw.replaceAll("\0", "").trim().replaceAll("outline: solid gray", "");

			fileUtil.unlink(cssFilePath, this.parallel());

			this.data.htmlFilePaths.parallelForEach((htmlFilePath, subcb, i) =>
			{
				const doc = domino.createWindow(htmlFilesRaw[i]).document;

				// Delete any links we have to the external CSS file
				Array.from(doc.querySelectorAll("link")).forEach(o =>
				{
					if((o.getAttribute("href") || "").includes("amigaguide.css"))
						o.remove();
				});

				// Create an inline STYLE tag and insert it into HEAD
				const style = doc.createElement("style");
				style.textContent = cssData;
				doc.querySelector("head").appendChild(style);	// eslint-disable-line unicorn/prefer-dom-node-append

				// Properly encode any hyperlinks (to handle files that have question marks in them, etc)
				Array.from(doc.querySelectorAll("a")).forEach(a => a.setAttribute("href", a.getAttribute("href").encodeURLPath()));

				// For whatever reason, grotag doesn't properly link the Index text to index.html, so we do it ourselves here
				const body = doc.querySelector("body");
				Array.from(body.childNodes).forEach(o =>
				{
					if(o.nodeType===3 && o.textContent.includes("| Index |"))
						o.textContent = ` | ${o.textContent.replaceAll("| Index |", "|")}`;
				});

				const topLink = doc.createElement("a");
				topLink.setAttribute("href", "index.html");
				topLink.textContent = "Index";
				body.insertBefore(topLink, body.childNodes[0]);

				fs.writeFile(htmlFilePath, doc.outerHTML, XU.UTF8, subcb);
			}, this.parallel());
		},
		cb
	);
};
*/
