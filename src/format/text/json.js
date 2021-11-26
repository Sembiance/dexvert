/*
import {Format} from "../../Format.js";

export class json extends Format
{
	name = "JavaScript Object Notation";
	website = "http://fileformats.archiveteam.org/wiki/JSON";
	ext = [".json"];
	mimeType = "application/json";
	untouched = true;
	confidenceAdjust = undefined;

	metaProviders = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	name             : "JavaScript Object Notation",
	website          : "http://fileformats.archiveteam.org/wiki/JSON",
	ext              : [".json"],
	mimeType         : "application/json",
	untouched        : true,
	confidenceAdjust : (state, matchType, curConfidence) => -(curConfidence-60)	// JSON is used for other formats (such as image/lottie) so we should always process same match types with a lower priority
};

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function loadFile()
		{
			fs.readFile(state.input.absolute, XU.UTF8, this);
		},
		function parseAsJSON(jsonRaw)
		{
			try
			{
				const result = JSON.parse(jsonRaw);
				if(result)
				{
					const meta = {};
					if(Array.isArray(result))
					{
						meta.type = "array";
						meta.entryCount = result.length;
					}
					else if(Object.isObject(result))
					{
						meta.type = "object";
						meta.keyCount = Object.keys(result).length;
					}
					else
					{
						meta.type = typeof result;
					}
					
					state.input.meta.json = meta;

					state.processed = true;
				}
			}
			catch(err) {}

			p.family.supportedInputMeta(state, p, this);
		},
		cb
	);
};

*/
