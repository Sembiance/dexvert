#!/usr/bin/node
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	util = require("util"),
	xmlJS = require("xml-js"),
	cmdUtil = require("@sembiance/xutil").cmd,
	tiptoe = require("tiptoe");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Will convert a trid def XML file to a magic output",
	opts    :
	{
		magic   : {desc : "Specify which 'Magic String' you want file to report it as", hasValue : true},
		autoAdd : {desc : "Automatically add to file_magic/dexvert-magic"}
	},
	args :
	[
		{argid : "inputTridXML", desc : "", required : true}
	]});

tiptoe(
	function loadXMLFile()
	{
		fs.readFile(argv.inputTridXML, XU.UTF8, this);
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
		fs.appendFile("/mnt/compendium/DevLab/dexvert/file_magic/dexvert-magic", `\n${lines.join("\n")}`, XU.UTF8, this);
	},
	XU.FINISH
);
