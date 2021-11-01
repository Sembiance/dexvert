"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://www.winehq.org/",
	gentooPackage  : "app-emulation/wine-vanilla",
	gentooUseFlags : "X alsa cups faudio fontconfig jpeg lcms mp3 nls opengl perl png realtime run-exes ssl threads truetype unwind xcomposite xinerama xml ",
	informational  : true
};

exports.bin = () => "winedump";
exports.args = (state, p, r, inPath=state.input.filePath) => (["dump", inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	let category = null;
	let subcat = null;

	const KEY_VAL_HEADERS = ["fileheader", "dosimage"];
	const ARRAY_HEADERS = ["optionalheader32bit", "datadirectory"];
	const NUMS =
	[
		"bytesOnLastPage", "numberOfPages", "relocations", "sizeOfHeader", "minExtraParagraphs", "maxExtraParagraphs", "overlayNumber", "offsetToExtHeader", "relocationFile",	// EXE
		"autoDataSegment", "numberOfSegments", "numberOfModrefs"	// DLL
	];
	const ARRAY_SUBCATS = ["characteristics"];
	(r.results || "").trim().split("\n").forEach(line =>
	{
		const lineCat = line.trimChars(":").trim().strip(" ()").toLowerCase();
		if([...KEY_VAL_HEADERS, ...ARRAY_HEADERS].includes(lineCat))
		{
			category = line.trimChars(" :").strip(" ()").toLowerCase();
			subcat = null;
		}
		else if(category)
		{
			const props = (line.match(/^\s*(?<key>[^:]+):\s+(?<val>.+)\s*$/) || {}).groups;
			const propValue = props ? props.val : line.trim();
			const propKey = props ? props.key.trim().strip("()-").toCamelCase() : null;

			if(propValue.length===0)
			{
				category = null;
				return;
			}

			if(KEY_VAL_HEADERS.includes(category))
			{
				if(!meta[category])
					meta[category] = {};

				if(subcat)
				{
					if(ARRAY_SUBCATS.includes(subcat))
						meta[category][subcat].push(propValue);
					else
						meta[category][subcat] = NUMS.includes(propKey) ? +propValue : propValue;
				}
				else if(ARRAY_SUBCATS.includes(propKey))
				{
					subcat = propKey;
					meta[category][subcat] = [];
				}
				else if(propKey)
				{
					meta[category][propKey] = NUMS.includes(propKey) ? +propValue : propValue;
				}
			}
			else
			{
				if(!meta[category])
					meta[category] = [];
				
				meta[category].push(propValue);
			}
		}
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
