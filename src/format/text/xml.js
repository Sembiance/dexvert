"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	xmlJS = require("xml-js");

exports.meta =
{
	name           : "Extensible Markup Language",
	website        : "http://fileformats.archiveteam.org/wiki/XML",
	ext            : [".xml"],
	forbidExtMatch : true,
	mimeType       : "application/xml",
	magic          : ["Extensible Markup Language", "Generic XML", /^XML .*document/],
	untouched      : true,
	hljsLang       : "xml"
};

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function loadFile()
		{
			fs.readFile(state.input.absolute, this);
		},
		function storeMeta(fileDataRaw)
		{
			try
			{
				const xmlData = xmlJS.xml2js(fileDataRaw);
				if(xmlData)
				{
					p.family.supportedInputMeta(state, p, this);
					return;
				}
			}
			catch(err) {}

			this();
		},
		cb
	);
};
