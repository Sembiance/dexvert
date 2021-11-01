/*
import {Format} from "../../Format.js";

export class ini extends Format
{
	name = "INI File";
	website = "http://fileformats.archiveteam.org/wiki/INI";
	ext = [".ini",".inf",".cfg",".conf",".nfo"];
	forbidExtMatch = [".cfg",".conf",".nfo"];
	magic = ["Generic INI configuration"];
	priority = 3;
	untouched = true;
	hljsLang = "ini";

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	C = require("../../C.js"),
	tiptoe = require("tiptoe");

exports.meta =
{
	name           : "INI File",
	website        : "http://fileformats.archiveteam.org/wiki/INI",
	ext            : [".ini", ".inf", ".cfg", ".conf", ".nfo"],
	forbidExtMatch : [".cfg", ".conf", ".nfo"],
	magic          : ["Generic INI configuration"],
	priority       : C.PRIORITY.LOW,
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
			const iniValidateData = p.util.program.getRan(state, "inivalidate")?.meta;
			if(!state.input.meta.text.verifiedAsText || !iniValidateData || !iniValidateData.valid)
			{
				state.processed = false;
				return this();
			}

			// Some INI file sections have periods at the start or end, which libconfini trims, so we handle that check here
			if(iniValidateData.sectionNames.some(sectionName => sectionName && (!iniRaw.includes(`[${sectionName}`) && !iniRaw.includes(`${sectionName}]`))))
			{
				if(state.verbose>=3)
					XU.log`Invalid INI file due to some section names not being present in file as [sectionName] ${iniValidateData.sectionNames}`;

				state.processed = false;
				return this();
			}

			state.input.meta.ini = {sections : iniValidateData.sectionNames};

			this();
		},
		cb
	);
};

*/
