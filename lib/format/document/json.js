"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	name      : "JavaScript Object Notation",
	website   : "http://fileformats.archiveteam.org/wiki/PDF",
	ext       : [".json"],
	mimeType  : "application/json",
	magic     : [/^JSON data$/],
	weakMagic : true
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
						meta.numEntries = result.length;
					}
					else if(Object.isObject(result))
					{
						meta.type = "object";
						meta.numKeys = Object.keys(result).length;
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

			this();
		},
		cb
	);
};
