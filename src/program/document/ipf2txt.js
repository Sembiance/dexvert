/*
import {Program} from "../../Program.js";

export class ipf2txt extends Program
{
	website = "https://github.com/Sembiance/dexvert";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	{Iconv} = require("iconv"),
	path = require("path");

exports.meta =
{
	website : "https://github.com/Sembiance/dexvert"
};

exports.dos = () => "IPF2TXT.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath, "80", ">", "OUTFILE.TXT"]);
exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function loadOutFile()
		{
			fs.readFile(path.join(state.cwd, "OUTFILE.TXT"), this);
		},
		function convertEncodingAndSave(outRaw)
		{
			// Files appear to be encoded in either CP866 or CP855 according to: https://base64.guru/tools/character-encoding
			let outTxt = outRaw.toString("UTF8");
			try
			{
				outTxt = (new Iconv("CP866", "UTF-8")).convert(outRaw);
			}
			catch(err)
			{
				outTxt = outRaw.toString("UTF8");
			}

			fs.writeFile(path.join(state.output.absolute, `${state.input.name}.txt`), outTxt, XU.UTF8, this);
		},
		cb
	);
};
*/
