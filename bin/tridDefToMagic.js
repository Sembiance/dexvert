#!/usr/bin/node
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	util = require("util"),
	xmlJS = require("xml-js"),
	{Command} = require("commander"),
	tiptoe = require("tiptoe");

const argv = new Command().description("Will convert a trid def XML file to a magic output").
	option("--magic <magicString>", "Specify which 'Magic String' you want file to report it as").
	option("--autoAdd", "Automatically add to file_magic/dexvert-magic").
	arguments("<inputTrid.xml>").
	parse(process.argv);

tiptoe(
	function loadXMLFile()
	{
		fs.readFile(argv.args[0], XU.UTF8, this);
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
