#!/usr/bin/node
"use strict";
/* eslint-disable no-underscore-dangle */

const XU = require("@sembiance/xu"),
	fs = require("fs"),
	util = require("util"),
	xmlJS = require("xml-js"),
	argv = require("minimist")(process.argv.slice(2), {boolean : true}),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

if(!argv.magic)
	process.exit(console.error("Usage: tridDefToMagic.js [--autoAdd] --magic=\"Your Magic String\" <newtype.trid.xml>"));

if(argv._.length===0 || !fileUtil.existsSync(`${argv._[0]}`))
	process.exit(console.error("Usage: tridDefToMagic.js [--autoAdd] --magic=\"Your Magic String\" <newtype.trid.xml>"));

tiptoe(
	function loadXMLFile()
	{
		fs.readFile(`${argv._[0]}`, XU.UTF8, this);
	},
	function processXMLFile(xmlFileRaw)
	{
		const lines = ["", `# ${argv.magic}`];
		const xmlData = xmlJS.xml2js(xmlFileRaw, {compact : true});
		xmlData.TrID.FrontBlock.Pattern.forEach((pat, i) =>
		{
			if(pat.Bytes)
				lines.push(util.format("%s%d\tstring/b\t\\x%s", (i>0 ? ">" : ""), pat.Pos._text, pat.Bytes._text.match(/../g).join("\\x")));
		});

		lines.push(`${lines.pop()}\t${argv.magic}`);

		const ext = (xmlData.TrID.Info.Ext._text || "").toLowerCase();
		if(ext.length>0 && ext.length<10)
			lines.push(`!:ext ${ext}`);

		console.log(lines.join("\n"));

		if(!argv.autoAdd)
			return this();

		console.log("\nAutomatically appending to my-magic...");
		fs.appendFile("/mnt/compendium/sys/magic/my-magic", `\n${lines.join("\n")}`, XU.UTF8, this);
	},
	XU.FINISH
);
