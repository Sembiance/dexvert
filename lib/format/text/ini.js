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
			p.util.program.run("inivalidate")(state, p, this.parallel());
		},
		function storeMeta(iniRaw)
		{
			const iniData = ini.parse(iniRaw);
			if(!iniData || Object.keys(iniData).length===0 || !state.input.meta.text.verifiedAsText || !p.util.program.getRan(state, "inivalidate")?.meta?.iniValidated)
			{
				state.processed = false;
				return this();
			}

			const sections = Object.keys(iniData);
			if(sections.some(section => !iniRaw.includes(`[${section}]`)))
			{
				state.processed = false;
				return this();
			}

			state.input.meta.ini = {sections};

			this();
		},
		cb
	);
};
