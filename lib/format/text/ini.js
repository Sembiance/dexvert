"use strict";
const XU = require("@sembiance/xu"),
	ini = require("ini"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

exports.meta =
{
	name           : "INI File",
	website        : "http://fileformats.archiveteam.org/wiki/INI",
	ext            : [".ini", ".cfg", ".conf"],
	forbidExtMatch : true,
	magic          : ["Generic INItialization configuration", "Windows SYSTEM.INI", "Windows WIN.INI", "Generic INI configuration"],
	untouched      : true,
	hljsLang       : "ini"
};

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function loadFile()
		{
			fs.readFile(state.input.absolute, XU.UTF8, this.parallel());
			p.family.supportedInputMeta(state, p, this.parallel());
		},
		function storeMeta(iniRaw)
		{
			// If the NPM ini package turns out to be too "loose", I could look into creating a C program to convert INI to JSON utiliznig this lib: https://github.com/madmurphy/libconfini
			const iniData = ini.parse(iniRaw);
			if(!iniData || Object.keys(iniData).length===0 || !state.input.meta.text.verifiedAsText)
				state.processed = false;
			else
				state.input.meta.ini = {sections : Object.keys(iniData)};

			this();
		},
		cb
	);
};
