/*
import {Format} from "../../Format.js";

export class csv extends Format
{
	name = "Comma Seperated Value File";
	website = "http://fileformats.archiveteam.org/wiki/CSV";
	ext = [".csv"];
	mimeType = "application/json";
	magic = ["CSV text"];
	priority = 3;

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	csv = require("csv-parser"),
	C = require("../../C.js"),
	fs = require("fs");

exports.meta =
{
	name      : "Comma Seperated Value File",
	website   : "http://fileformats.archiveteam.org/wiki/CSV",
	ext       : [".csv"],
	mimeType  : "application/json",
	magic     : ["CSV text"],
	priority  : C.PRIORITY.LOW
};

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function loadFile()
		{
			const csvRows = [];
			this.capture();	// Might get an error along the way, sometimes at the end, so just eat it and continue along :)
			fs.createReadStream(state.input.absolute).pipe(csv()).on("data", row => csvRows.push(row)).on("end", () => this(undefined, csvRows));
		},
		function storeMeta(err, csvRows)
		{
			if(csvRows && csvRows.length>0)
			{
				state.input.meta.csv = {};
				state.input.meta.csv.keys = csvRows.flatMap(csvRow => Object.keys(csvRow)).unique();
				state.input.meta.csv.entryCount = csvRows.length;

				state.processed = true;
			}

			p.family.supportedInputMeta(state, p, this);
		},
		cb
	);
};

*/
