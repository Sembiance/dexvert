"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Amiga IFF Catalog",
	website        : "http://fileformats.archiveteam.org/wiki/IFF",
	ext            : [".catalog"],
	forbidExtMatch : true,
	magic          : ["IFF data, CTLG message catalog", "Amiga Catalog translation format"],
	unsupported    : true,
	notes          : "Contains strings used by programs. Not currently enabled as my parser isn't quite right and I don't feel like debugging it more."
};


/* eslint-disable object-shorthand */
/*
	//path = require("path"),
	//{Parser} = require("binary-parser"),
	//fs = require("fs");
exports.steps =
[
	() => (state, p, cb) =>
	{
		const headerFormat = new Parser().
			string("iffType", {length : 4}).
			uint32("dataSize").
			string("fileType", {length : 4});

		const fverEntry = new Parser().string("signature", {length : "chunkSize", stripNull : true, encoding : "iso-8859-2"});
		const langEntry = new Parser().string("language", {length : "chunkSize", stripNull : true, encoding : "iso-8859-2"});

		const strsString = new Parser().
			uint32("strid").
			uint32("strLength", {formatter : function(strLength) { return strLength+(4-(strLength%4)); }}).
			string("str", {length : "strLength", stripNull : true, encoding : "iso-8859-2", formatter : function(str) { return str.charAt(1)==="\0" ? str.substring(2) : str; }});
		const strsEntry = new Parser().
			array("strings", {type : strsString, readUntil : "eof"});

		const unknownEntry = new Parser().buffer("chunkData", { length : "chunkSize"});
		// CSET is "codeset" but don't really know how to handle it. See here for info: http://aminet.net/package/util/conv/CTLG2CT

		const entryFormat = new Parser().
			string("chunkid", {length : 4}).
			uint32("chunkSize").
			choice({
				tag : function() { return ["FVER", "LANG", "STRS"].indexOf(this.chunkid)+1 || -1; },
				choices :
				{
					1 : fverEntry,
					2 : langEntry,
					3 : strsEntry
				},
				defaultChoice : unknownEntry
			});

		const ctlgFormat = new Parser().
			endianess("big").
			nest("header", {type : headerFormat}).
			array("entries", {type : entryFormat, readUntil : "eof"});

		const result = ctlgFormat.parse(fs.readFileSync(state.input.absolute));
		if(result.header.iffType!=="FORM" || result.header.fileType!=="CTLG")
			return cb();

		fs.writeFile(path.join(state.output.absolute, `${state.input.name}.json`), JSON.stringify(result), XU.UTF8, cb);
	}
];
*/
